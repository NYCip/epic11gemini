'use client'

import { useSession } from 'next-auth/react'
import { SystemStatus } from '@/components/dashboard/SystemStatus'
import { BoardDecisions } from '@/components/dashboard/BoardDecisions'
import { EmergencyOverride } from '@/components/override/EmergencyOverride'
import { Activity, Shield, Users, Brain } from 'lucide-react'

export default function DashboardPage() {
  const { data: session } = useSession()
  
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-white">
          Welcome, {session?.user?.name}
        </h1>
        <div className="text-sm text-gray-400">
          Role: <span className="text-blue-400 font-semibold">{session?.user?.role}</span>
        </div>
      </div>
      
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatCard
          title="System Status"
          value="ACTIVE"
          icon={<Activity className="h-8 w-8" />}
          color="green"
        />
        <StatCard
          title="Board Members"
          value="11/11"
          icon={<Brain className="h-8 w-8" />}
          color="blue"
        />
        <StatCard
          title="Active Users"
          value="3"
          icon={<Users className="h-8 w-8" />}
          color="purple"
        />
        <StatCard
          title="Security Level"
          value="MAXIMUM"
          icon={<Shield className="h-8 w-8" />}
          color="yellow"
        />
      </div>
      
      {/* Emergency Override - Only for Admins */}
      {session?.user?.role === 'admin' && (
        <EmergencyOverride />
      )}
      
      {/* Main Dashboard Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SystemStatus />
        <BoardDecisions />
      </div>
    </div>
  )
}

function StatCard({ title, value, icon, color }: {
  title: string
  value: string
  icon: React.ReactNode
  color: 'green' | 'blue' | 'purple' | 'yellow'
}) {
  const colorClasses = {
    green: 'text-green-500 bg-green-500/10 border-green-500/20',
    blue: 'text-blue-500 bg-blue-500/10 border-blue-500/20',
    purple: 'text-purple-500 bg-purple-500/10 border-purple-500/20',
    yellow: 'text-yellow-500 bg-yellow-500/10 border-yellow-500/20'
  }
  
  return (
    <div className={`p-6 rounded-lg border ${colorClasses[color]}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-400">{title}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
        </div>
        <div className={colorClasses[color].split(' ')[0]}>
          {icon}
        </div>
      </div>
    </div>
  )
}