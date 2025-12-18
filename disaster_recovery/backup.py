#!/usr/bin/env python3
"""
JoveHeal Complete Backup Script
================================
Creates a full backup of all databases and critical data for disaster recovery.

Backs up:
- PostgreSQL database (schema + all data)
- ChromaDB vector database (complete directory)
- Knowledge base metadata
- Environment configuration template

Usage:
    python disaster_recovery/backup.py

Output:
    backups/joveheal_complete_YYYY-MM-DD_HH-MM-SS.tar.gz
"""

import os
import sys
import json
import shutil
import tarfile
import subprocess
from datetime import datetime
from pathlib import Path


class JoveHealBackup:
    def __init__(self):
        self.timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.backup_dir = Path('backups') / f'joveheal_backup_{self.timestamp}'
        self.final_archive = Path('backups') / f'joveheal_complete_{self.timestamp}.tar.gz'
        self.results = {}
        
    def log(self, message, level="INFO"):
        prefix = {"INFO": "  ", "OK": "✓ ", "WARN": "⚠ ", "ERROR": "✗ "}
        print(f"{prefix.get(level, '  ')}{message}")
    
    def ensure_directories(self):
        Path('backups').mkdir(exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
    def backup_postgresql(self):
        """Backup PostgreSQL database with full schema and data.
        
        Streams pg_dump output directly to file to avoid memory issues
        with large databases.
        """
        self.log("Backing up PostgreSQL database...")
        
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            self.log("DATABASE_URL not found - skipping PostgreSQL", "WARN")
            self.results['postgresql'] = {'status': 'skipped', 'reason': 'DATABASE_URL not set'}
            return False
        
        output_file = self.backup_dir / 'postgresql.sql'
        
        try:
            with open(output_file, 'wb') as f:
                result = subprocess.run(
                    ['pg_dump', database_url, '--no-owner', '--no-acl', '--clean', '--if-exists'],
                    stdout=f,
                    stderr=subprocess.PIPE,
                    timeout=600
                )
            
            if result.returncode == 0:
                size = output_file.stat().st_size
                self.log(f"PostgreSQL: {self._format_size(size)}", "OK")
                self.results['postgresql'] = {'status': 'success', 'file': str(output_file), 'size': size}
                return True
            else:
                error_msg = result.stderr.decode('utf-8', errors='replace') if result.stderr else 'Unknown error'
                self.log(f"PostgreSQL backup failed: {error_msg}", "ERROR")
                self.results['postgresql'] = {'status': 'failed', 'error': error_msg}
                return False
                
        except subprocess.TimeoutExpired:
            self.log("PostgreSQL backup timed out (10 min limit)", "ERROR")
            self.results['postgresql'] = {'status': 'failed', 'error': 'timeout'}
            return False
        except Exception as e:
            self.log(f"PostgreSQL backup error: {e}", "ERROR")
            self.results['postgresql'] = {'status': 'failed', 'error': str(e)}
            return False
    
    def backup_chromadb(self):
        """Backup ChromaDB vector database directory."""
        self.log("Backing up ChromaDB vector database...")
        
        vector_db_path = Path('vector_db')
        if not vector_db_path.exists():
            self.log("vector_db directory not found - skipping", "WARN")
            self.results['chromadb'] = {'status': 'skipped', 'reason': 'directory not found'}
            return False
        
        try:
            dest = self.backup_dir / 'vector_db'
            shutil.copytree(vector_db_path, dest)
            size = sum(f.stat().st_size for f in dest.rglob('*') if f.is_file())
            self.log(f"ChromaDB: {self._format_size(size)}", "OK")
            self.results['chromadb'] = {'status': 'success', 'path': str(dest), 'size': size}
            return True
        except Exception as e:
            self.log(f"ChromaDB backup error: {e}", "ERROR")
            self.results['chromadb'] = {'status': 'failed', 'error': str(e)}
            return False
    
    def backup_knowledge_base(self):
        """Backup knowledge base metadata and documents."""
        self.log("Backing up knowledge base metadata...")
        
        kb_path = Path('knowledge_base')
        if not kb_path.exists():
            self.log("knowledge_base directory not found - skipping", "WARN")
            self.results['knowledge_base'] = {'status': 'skipped', 'reason': 'directory not found'}
            return False
        
        try:
            dest = self.backup_dir / 'knowledge_base'
            shutil.copytree(kb_path, dest)
            size = sum(f.stat().st_size for f in dest.rglob('*') if f.is_file())
            self.log(f"Knowledge Base: {self._format_size(size)}", "OK")
            self.results['knowledge_base'] = {'status': 'success', 'path': str(dest), 'size': size}
            return True
        except Exception as e:
            self.log(f"Knowledge base backup error: {e}", "ERROR")
            self.results['knowledge_base'] = {'status': 'failed', 'error': str(e)}
            return False
    
    def backup_somera_content(self):
        """Backup SOMERA coaching content directory."""
        self.log("Backing up SOMERA content...")
        
        somera_path = Path('somera_content')
        if not somera_path.exists():
            self.log("somera_content directory not found - skipping", "WARN")
            self.results['somera_content'] = {'status': 'skipped', 'reason': 'directory not found'}
            return False
        
        try:
            dest = self.backup_dir / 'somera_content'
            shutil.copytree(somera_path, dest)
            size = sum(f.stat().st_size for f in dest.rglob('*') if f.is_file())
            self.log(f"SOMERA Content: {self._format_size(size)}", "OK")
            self.results['somera_content'] = {'status': 'success', 'path': str(dest), 'size': size}
            return True
        except Exception as e:
            self.log(f"SOMERA content backup error: {e}", "ERROR")
            self.results['somera_content'] = {'status': 'failed', 'error': str(e)}
            return False
    
    def create_env_template(self):
        """Create environment variables template (without actual secrets)."""
        self.log("Creating environment template...")
        
        env_vars = {
            'required_secrets': [
                'DATABASE_URL',
                'OPENAI_API_KEY',
                'NEXTAUTH_SECRET',
                'NEXTAUTH_URL',
                'GOOGLE_CLIENT_ID',
                'GOOGLE_CLIENT_SECRET',
                'SESSION_SECRET',
            ],
            'optional_env_vars': [
                'INTERNAL_API_KEY',
                'ADMIN_EMAILS',
                'DASHBOARD_EMAIL',
                'DASHBOARD_PASSWORD',
                'RACEN_PERSONA_MODE',
            ],
            'notes': {
                'DATABASE_URL': 'PostgreSQL connection string (format: postgresql://user:pass@host:port/db)',
                'OPENAI_API_KEY': 'OpenAI API key for LLM functionality',
                'NEXTAUTH_SECRET': 'Random string for NextAuth session encryption',
                'NEXTAUTH_URL': 'Full URL of the deployed application',
                'GOOGLE_CLIENT_ID': 'Google OAuth client ID',
                'GOOGLE_CLIENT_SECRET': 'Google OAuth client secret',
            },
            'backup_timestamp': self.timestamp,
        }
        
        template_file = self.backup_dir / 'env_template.json'
        template_file.write_text(json.dumps(env_vars, indent=2))
        self.log("Environment template created", "OK")
        self.results['env_template'] = {'status': 'success', 'file': str(template_file)}
        return True
    
    def create_restore_script(self):
        """Create a restore script for the backup."""
        self.log("Creating restore script...")
        
        restore_script = '''#!/bin/bash
# JoveHeal Restore Script
# Generated: {timestamp}
#
# Usage:
#   1. Extract the backup archive
#   2. Set required environment variables (see env_template.json)
#   3. Run: bash restore.sh
#

echo "=========================================="
echo "  JoveHeal Restore Script"
echo "=========================================="

# Check for DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL environment variable not set!"
    echo "Please set DATABASE_URL to your PostgreSQL connection string."
    exit 1
fi

# Restore PostgreSQL
if [ -f "postgresql.sql" ]; then
    echo "[1/3] Restoring PostgreSQL database..."
    psql "$DATABASE_URL" < postgresql.sql
    if [ $? -eq 0 ]; then
        echo "      PostgreSQL restored successfully!"
    else
        echo "      ERROR: PostgreSQL restore failed!"
        exit 1
    fi
else
    echo "[1/3] No PostgreSQL backup found - skipping"
fi

# Restore ChromaDB
if [ -d "vector_db" ]; then
    echo "[2/3] Restoring ChromaDB vector database..."
    rm -rf ../vector_db 2>/dev/null
    cp -r vector_db ../
    echo "      ChromaDB restored successfully!"
else
    echo "[2/3] No ChromaDB backup found - skipping"
fi

# Restore Knowledge Base
if [ -d "knowledge_base" ]; then
    echo "[3/3] Restoring knowledge base..."
    rm -rf ../knowledge_base 2>/dev/null
    cp -r knowledge_base ../
    echo "      Knowledge base restored successfully!"
else
    echo "[3/3] No knowledge base backup found - skipping"
fi

echo ""
echo "=========================================="
echo "  RESTORE COMPLETE"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Set all environment variables from env_template.json"
echo "2. Run: npm install && npm run build"
echo "3. Run: pip install -r requirements.txt"
echo "4. Start the application"
echo ""
'''.format(timestamp=self.timestamp)
        
        restore_file = self.backup_dir / 'restore.sh'
        restore_file.write_text(restore_script)
        restore_file.chmod(0o755)
        self.log("Restore script created", "OK")
        self.results['restore_script'] = {'status': 'success', 'file': str(restore_file)}
        return True
    
    def create_archive(self):
        """Create final compressed archive."""
        self.log("Creating compressed archive...")
        
        try:
            with tarfile.open(self.final_archive, 'w:gz') as tar:
                tar.add(self.backup_dir, arcname=self.backup_dir.name)
            
            shutil.rmtree(self.backup_dir)
            
            size = self.final_archive.stat().st_size
            self.log(f"Archive: {self._format_size(size)}", "OK")
            self.results['archive'] = {'status': 'success', 'file': str(self.final_archive), 'size': size}
            return True
        except Exception as e:
            self.log(f"Archive creation failed: {e}", "ERROR")
            self.results['archive'] = {'status': 'failed', 'error': str(e)}
            return False
    
    def save_manifest(self):
        """Save backup manifest with results."""
        manifest_file = Path('backups') / f'manifest_{self.timestamp}.json'
        manifest = {
            'timestamp': self.timestamp,
            'archive': str(self.final_archive),
            'results': self.results,
        }
        manifest_file.write_text(json.dumps(manifest, indent=2))
        self.log(f"Manifest saved: {manifest_file}", "OK")
    
    def _format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def run(self):
        """Execute full backup procedure."""
        print("=" * 50)
        print("  JoveHeal Complete Backup")
        print("=" * 50)
        print(f"  Timestamp: {self.timestamp}")
        print("=" * 50)
        print()
        
        self.ensure_directories()
        
        self.backup_postgresql()
        self.backup_chromadb()
        self.backup_knowledge_base()
        self.backup_somera_content()
        self.create_env_template()
        self.create_restore_script()
        self.create_archive()
        self.save_manifest()
        
        print()
        print("=" * 50)
        print("  BACKUP COMPLETE")
        print("=" * 50)
        print()
        print(f"  Archive: {self.final_archive}")
        print()
        print("  To download:")
        print("  1. Open 'backups' folder in Replit file browser")
        print("  2. Right-click the .tar.gz file")
        print("  3. Click 'Download'")
        print()
        print("=" * 50)
        
        return self.results


if __name__ == '__main__':
    backup = JoveHealBackup()
    backup.run()
