'use client';

import { useState, useEffect } from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
} from 'recharts';

interface SomeraStats {
  totalCalls: number;
  totalMessages: number;
  avgLatency: number;
  peakReadiness: number;
  avgReadiness: number;
  bookingRate: number;
  latencyTrends: { date: string; min: number; avg: number; max: number }[];
  readinessDistribution: { explore: number; transition: number; guide: number };
}

interface VoiceCall {
  callId: string;
  startedAt: string;
  endedAt: string;
  messageCount: number;
  avgLatency: number | null;
  peakReadiness: number;
  hadBooking: boolean;
}

interface VoiceMessage {
  role: string;
  content: string;
  readinessScore: number | null;
  readinessRecommendation: string | null;
  latencyMs: number | null;
  closureType: string | null;
  timestamp: string;
}

interface CallDetail {
  callId: string;
  messages: VoiceMessage[];
}

const PURPLE_COLORS = ['#a855f7', '#c084fc', '#d8b4fe'];

export default function SomeraAdminDashboard() {
  const [activeTab, setActiveTab] = useState<'analytics' | 'transcripts' | 'insights'>('analytics');
  const [stats, setStats] = useState<SomeraStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('30d');
  
  const [calls, setCalls] = useState<VoiceCall[]>([]);
  const [callsLoading, setCallsLoading] = useState(false);
  const [selectedCall, setSelectedCall] = useState<string | null>(null);
  const [callDetail, setCallDetail] = useState<CallDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  useEffect(() => {
    if (activeTab === 'analytics' || activeTab === 'insights') {
      fetchStats();
    } else if (activeTab === 'transcripts') {
      fetchCalls();
    }
  }, [timeRange, activeTab]);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const res = await fetch(`/api/admin/somera/stats?range=${timeRange}`);
      if (res.ok) {
        const data = await res.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
    setLoading(false);
  };

  const fetchCalls = async () => {
    setCallsLoading(true);
    try {
      const res = await fetch(`/api/admin/somera/calls?range=${timeRange}`);
      if (res.ok) {
        const data = await res.json();
        setCalls(data.calls || []);
      }
    } catch (error) {
      console.error('Failed to fetch calls:', error);
    }
    setCallsLoading(false);
  };

  const fetchCallDetail = async (callId: string) => {
    setDetailLoading(true);
    setSelectedCall(callId);
    try {
      const res = await fetch(`/api/admin/somera/calls/${encodeURIComponent(callId)}`);
      if (res.ok) {
        const data = await res.json();
        setCallDetail(data);
      }
    } catch (error) {
      console.error('Failed to fetch call detail:', error);
    }
    setDetailLoading(false);
  };

  const formatDate = (dateStr: string) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getReadinessBadge = (score: number | null) => {
    if (score === null) return null;
    const percent = Math.round(score * 100);
    let color = 'bg-blue-500/20 text-blue-400';
    let label = 'Explore';
    
    if (score >= 0.35) {
      color = 'bg-green-500/20 text-green-400';
      label = 'Guide';
    } else if (score >= 0.20) {
      color = 'bg-yellow-500/20 text-yellow-400';
      label = 'Transition';
    }
    
    return (
      <span className={`px-2 py-0.5 rounded-full text-xs ${color}`}>
        {label} ({percent}%)
      </span>
    );
  };

  const formatLatency = (ms: number | null) => {
    if (ms === null) return '-';
    if (ms < 1000) return `${Math.round(ms)}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900/20 to-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-purple-500/20 rounded-full flex items-center justify-center">
              <svg className="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              </svg>
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white">SOMERA Voice Analytics</h1>
              <p className="text-gray-400 mt-1">Voice coaching performance dashboard</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex gap-2">
              {['24h', '7d', '30d'].map((range) => (
                <button
                  key={range}
                  onClick={() => setTimeRange(range)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                    timeRange === range
                      ? 'bg-purple-500 text-white shadow-lg shadow-purple-500/30'
                      : 'bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white'
                  }`}
                >
                  {range === '24h' ? 'Last 24h' : range === '7d' ? 'Last 7 days' : 'Last 30 days'}
                </button>
              ))}
            </div>
            <a
              href="/admin/dashboard"
              className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-400 hover:text-white rounded-lg text-sm transition-colors"
            >
              Jovee Dashboard
            </a>
          </div>
        </div>

        <div className="flex gap-4 mb-8">
          <button
            onClick={() => setActiveTab('analytics')}
            className={`px-6 py-3 rounded-xl font-medium transition-all flex items-center gap-2 ${
              activeTab === 'analytics'
                ? 'bg-purple-500 text-white'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            Analytics
          </button>
          <button
            onClick={() => setActiveTab('transcripts')}
            className={`px-6 py-3 rounded-xl font-medium transition-all flex items-center gap-2 ${
              activeTab === 'transcripts'
                ? 'bg-purple-500 text-white'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
            Transcripts
          </button>
          <button
            onClick={() => setActiveTab('insights')}
            className={`px-6 py-3 rounded-xl font-medium transition-all flex items-center gap-2 ${
              activeTab === 'insights'
                ? 'bg-purple-500 text-white'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            Insights
          </button>
        </div>

        {activeTab === 'analytics' && (
          <AnalyticsView stats={stats} loading={loading} formatLatency={formatLatency} />
        )}
        {activeTab === 'transcripts' && (
          <TranscriptsView
            calls={calls}
            callsLoading={callsLoading}
            selectedCall={selectedCall}
            callDetail={callDetail}
            detailLoading={detailLoading}
            onSelectCall={fetchCallDetail}
            formatDate={formatDate}
            getReadinessBadge={getReadinessBadge}
            formatLatency={formatLatency}
          />
        )}
        {activeTab === 'insights' && (
          <InsightsView stats={stats} loading={loading} />
        )}
      </div>
    </div>
  );
}

function StatCard({ title, value, subtitle, icon, color = 'purple' }: { 
  title: string; 
  value: string; 
  subtitle?: string;
  icon: React.ReactNode;
  color?: 'purple' | 'green' | 'blue' | 'yellow';
}) {
  const colorClasses = {
    purple: 'bg-purple-500/20 text-purple-400',
    green: 'bg-green-500/20 text-green-400',
    blue: 'bg-blue-500/20 text-blue-400',
    yellow: 'bg-yellow-500/20 text-yellow-400',
  };
  
  return (
    <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700/50">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-gray-400 text-sm">{title}</p>
          <p className="text-3xl font-bold text-white mt-2">{value}</p>
          {subtitle && <p className="text-gray-500 text-sm mt-1">{subtitle}</p>}
        </div>
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${colorClasses[color]}`}>
          {icon}
        </div>
      </div>
    </div>
  );
}

function AnalyticsView({ stats, loading, formatLatency }: { 
  stats: SomeraStats | null; 
  loading: boolean;
  formatLatency: (ms: number | null) => string;
}) {
  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-400"></div>
      </div>
    );
  }

  const hasData = stats && stats.totalCalls > 0;

  const readinessData = stats ? [
    { name: 'Explore', value: stats.readinessDistribution.explore, color: '#3b82f6' },
    { name: 'Transition', value: stats.readinessDistribution.transition, color: '#eab308' },
    { name: 'Guide', value: stats.readinessDistribution.guide, color: '#22c55e' },
  ] : [];

  return (
    <>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Total Calls"
          value={stats?.totalCalls?.toString() || '0'}
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
            </svg>
          }
        />
        <StatCard
          title="Total Messages"
          value={stats?.totalMessages?.toString() || '0'}
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          }
          color="blue"
        />
        <StatCard
          title="Avg Response Time"
          value={formatLatency(stats?.avgLatency || 0)}
          subtitle="Target: < 3s"
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
          color="yellow"
        />
        <StatCard
          title="Booking Rate"
          value={`${stats?.bookingRate || 0}%`}
          subtitle="Discovery call requests"
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          }
          color="green"
        />
      </div>

      {!hasData ? (
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-12 border border-gray-700/50 text-center">
          <svg className="w-16 h-16 mx-auto text-gray-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
          </svg>
          <h3 className="text-xl font-semibold text-white mb-2">No Voice Calls Yet</h3>
          <p className="text-gray-400">Make some voice calls with SOMERA to see analytics here.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700/50">
            <h2 className="text-xl font-semibold text-white mb-4">Response Latency Trends</h2>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={stats?.latencyTrends || []}>
                  <defs>
                    <linearGradient id="colorLatency" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#a855f7" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#a855f7" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="date" stroke="#9ca3af" fontSize={12} />
                  <YAxis stroke="#9ca3af" fontSize={12} tickFormatter={(v) => `${(v/1000).toFixed(1)}s`} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1f2937',
                      border: '1px solid #374151',
                      borderRadius: '8px',
                      color: '#fff',
                    }}
                    formatter={(value: number) => [`${(value/1000).toFixed(2)}s`, '']}
                  />
                  <Area
                    type="monotone"
                    dataKey="avg"
                    stroke="#a855f7"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#colorLatency)"
                    name="Avg Latency"
                  />
                  <Line type="monotone" dataKey="min" stroke="#22c55e" strokeWidth={1} dot={false} name="Min" />
                  <Line type="monotone" dataKey="max" stroke="#ef4444" strokeWidth={1} dot={false} name="Max" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700/50">
            <h2 className="text-xl font-semibold text-white mb-4">Readiness Distribution</h2>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={readinessData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={90}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {readinessData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1f2937',
                      border: '1px solid #374151',
                      borderRadius: '8px',
                      color: '#fff',
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex justify-center gap-4 mt-4">
              {readinessData.map((item) => (
                <div key={item.name} className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                  <span className="text-sm text-gray-400">{item.name}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </>
  );
}

function TranscriptsView({
  calls,
  callsLoading,
  selectedCall,
  callDetail,
  detailLoading,
  onSelectCall,
  formatDate,
  getReadinessBadge,
  formatLatency,
}: {
  calls: VoiceCall[];
  callsLoading: boolean;
  selectedCall: string | null;
  callDetail: CallDetail | null;
  detailLoading: boolean;
  onSelectCall: (callId: string) => void;
  formatDate: (dateStr: string) => string;
  getReadinessBadge: (score: number | null) => React.ReactNode;
  formatLatency: (ms: number | null) => string;
}) {
  if (callsLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-400"></div>
      </div>
    );
  }

  if (calls.length === 0) {
    return (
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-12 border border-gray-700/50 text-center">
        <svg className="w-16 h-16 mx-auto text-gray-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
        <h3 className="text-xl font-semibold text-white mb-2">No Transcripts</h3>
        <p className="text-gray-400">Voice call transcripts will appear here.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-1 bg-gray-800/50 backdrop-blur-sm rounded-2xl p-4 border border-gray-700/50 max-h-[calc(100vh-280px)] overflow-y-auto">
        <h2 className="text-lg font-semibold text-white mb-4 px-2">Call History</h2>
        <div className="space-y-2">
          {calls.map((call) => (
            <button
              key={call.callId}
              onClick={() => onSelectCall(call.callId)}
              className={`w-full text-left p-4 rounded-xl transition-all ${
                selectedCall === call.callId
                  ? 'bg-purple-500/20 border border-purple-500/50'
                  : 'bg-gray-700/30 hover:bg-gray-700/50 border border-transparent'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-400">{formatDate(call.startedAt)}</span>
                {call.hadBooking && (
                  <span className="px-2 py-0.5 rounded-full text-xs bg-green-500/20 text-green-400">
                    Booking
                  </span>
                )}
              </div>
              <div className="flex items-center justify-between">
                <span className="text-white font-medium">{call.messageCount} messages</span>
                <span className="text-sm text-gray-500">
                  Peak: {Math.round(call.peakReadiness * 100)}%
                </span>
              </div>
              {call.avgLatency && (
                <div className="text-xs text-gray-500 mt-1">
                  Avg latency: {formatLatency(call.avgLatency)}
                </div>
              )}
            </button>
          ))}
        </div>
      </div>

      <div className="lg:col-span-2 bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700/50 max-h-[calc(100vh-280px)] overflow-y-auto">
        {!selectedCall ? (
          <div className="flex items-center justify-center h-full text-gray-500">
            Select a call to view the transcript
          </div>
        ) : detailLoading ? (
          <div className="flex items-center justify-center h-full">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-purple-400"></div>
          </div>
        ) : callDetail ? (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-white mb-4">Conversation Transcript</h2>
            {callDetail.messages.map((msg, idx) => (
              <div
                key={idx}
                className={`p-4 rounded-xl ${
                  msg.role === 'user'
                    ? 'bg-blue-500/10 border border-blue-500/20 ml-0 mr-12'
                    : 'bg-purple-500/10 border border-purple-500/20 ml-12 mr-0'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className={`text-xs font-medium ${
                    msg.role === 'user' ? 'text-blue-400' : 'text-purple-400'
                  }`}>
                    {msg.role === 'user' ? 'User' : 'SOMERA'}
                  </span>
                  <div className="flex items-center gap-2">
                    {msg.role === 'user' && getReadinessBadge(msg.readinessScore)}
                    {msg.role === 'assistant' && msg.latencyMs && (
                      <span className="text-xs text-gray-500">
                        {formatLatency(msg.latencyMs)}
                      </span>
                    )}
                  </div>
                </div>
                <p className="text-gray-200 text-sm">{msg.content}</p>
                {msg.closureType && (
                  <span className="inline-block mt-2 px-2 py-0.5 rounded-full text-xs bg-gray-700 text-gray-400">
                    {msg.closureType}
                  </span>
                )}
              </div>
            ))}
          </div>
        ) : null}
      </div>
    </div>
  );
}

function InsightsView({ stats, loading }: { stats: SomeraStats | null; loading: boolean }) {
  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-400"></div>
      </div>
    );
  }

  const hasData = stats && stats.totalCalls > 0;

  if (!hasData) {
    return (
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-12 border border-gray-700/50 text-center">
        <svg className="w-16 h-16 mx-auto text-gray-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
        <h3 className="text-xl font-semibold text-white mb-2">No Insights Yet</h3>
        <p className="text-gray-400">Coaching insights will appear after more voice calls.</p>
      </div>
    );
  }

  const totalReadiness = (stats?.readinessDistribution.explore || 0) + 
                        (stats?.readinessDistribution.transition || 0) + 
                        (stats?.readinessDistribution.guide || 0);
  
  const explorePercent = totalReadiness > 0 ? Math.round((stats?.readinessDistribution.explore || 0) / totalReadiness * 100) : 0;
  const transitionPercent = totalReadiness > 0 ? Math.round((stats?.readinessDistribution.transition || 0) / totalReadiness * 100) : 0;
  const guidePercent = totalReadiness > 0 ? Math.round((stats?.readinessDistribution.guide || 0) / totalReadiness * 100) : 0;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700/50">
        <h2 className="text-xl font-semibold text-white mb-6">Coaching Metrics</h2>
        <div className="space-y-6">
          <div>
            <div className="flex justify-between mb-2">
              <span className="text-gray-400">Average Readiness Score</span>
              <span className="text-white font-semibold">{stats?.avgReadiness || 0}%</span>
            </div>
            <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
              <div 
                className="h-full bg-purple-500 rounded-full transition-all duration-500"
                style={{ width: `${stats?.avgReadiness || 0}%` }}
              />
            </div>
          </div>
          <div>
            <div className="flex justify-between mb-2">
              <span className="text-gray-400">Peak Readiness Achieved</span>
              <span className="text-white font-semibold">{stats?.peakReadiness || 0}%</span>
            </div>
            <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
              <div 
                className="h-full bg-green-500 rounded-full transition-all duration-500"
                style={{ width: `${stats?.peakReadiness || 0}%` }}
              />
            </div>
          </div>
          <div>
            <div className="flex justify-between mb-2">
              <span className="text-gray-400">Booking Conversion Rate</span>
              <span className="text-white font-semibold">{stats?.bookingRate || 0}%</span>
            </div>
            <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
              <div 
                className="h-full bg-yellow-500 rounded-full transition-all duration-500"
                style={{ width: `${stats?.bookingRate || 0}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700/50">
        <h2 className="text-xl font-semibold text-white mb-6">Readiness Zone Analysis</h2>
        <div className="space-y-4">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-blue-500/20 rounded-xl flex items-center justify-center">
              <span className="text-2xl font-bold text-blue-400">{explorePercent}%</span>
            </div>
            <div>
              <h3 className="text-white font-medium">Explore Zone (0-20%)</h3>
              <p className="text-gray-500 text-sm">Users still discovering their needs</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-yellow-500/20 rounded-xl flex items-center justify-center">
              <span className="text-2xl font-bold text-yellow-400">{transitionPercent}%</span>
            </div>
            <div>
              <h3 className="text-white font-medium">Transition Zone (20-35%)</h3>
              <p className="text-gray-500 text-sm">Building clarity and understanding</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-green-500/20 rounded-xl flex items-center justify-center">
              <span className="text-2xl font-bold text-green-400">{guidePercent}%</span>
            </div>
            <div>
              <h3 className="text-white font-medium">Guide Zone (35%+)</h3>
              <p className="text-gray-500 text-sm">Ready for actionable guidance</p>
            </div>
          </div>
        </div>
      </div>

      <div className="lg:col-span-2 bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700/50">
        <h2 className="text-xl font-semibold text-white mb-4">Readiness Thresholds</h2>
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center p-4 bg-blue-500/10 rounded-xl border border-blue-500/20">
            <p className="text-3xl font-bold text-blue-400">20%</p>
            <p className="text-gray-400 text-sm mt-1">Transition Threshold</p>
            <p className="text-gray-500 text-xs mt-2">Start blending questions with light guidance</p>
          </div>
          <div className="text-center p-4 bg-yellow-500/10 rounded-xl border border-yellow-500/20">
            <p className="text-3xl font-bold text-yellow-400">35%</p>
            <p className="text-gray-400 text-sm mt-1">Guidance Threshold</p>
            <p className="text-gray-500 text-xs mt-2">Shift to actionable recommendations</p>
          </div>
          <div className="text-center p-4 bg-green-500/10 rounded-xl border border-green-500/20">
            <p className="text-3xl font-bold text-green-400">50%+</p>
            <p className="text-gray-400 text-sm mt-1">High Readiness</p>
            <p className="text-gray-500 text-xs mt-2">Full coaching mode activated</p>
          </div>
        </div>
      </div>
    </div>
  );
}
