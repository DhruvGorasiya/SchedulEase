'use client'

import { UserProfile, useUser } from "@clerk/nextjs"
import { motion } from "framer-motion"
import { FaEnvelope, FaUser } from "react-icons/fa"

export default function ProfilePage() {
  const { user, isLoaded } = useUser()

  if (!isLoaded) {
    return (
      <div className="flex justify-center items-center min-h-screen bg-gray-50">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-gray-900"></div>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            Please create account or sign in to view your profile
          </h2>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-2xl mx-auto">
        {/* Simple Header */}
        <h1 className="text-3xl font-semibold text-gray-900 mb-8">
          {user?.firstName} {user?.lastName}
        </h1>

        {/* Info Cards */}
        <div className="space-y-4">
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center space-x-3">
              <FaEnvelope className="text-gray-400 w-5 h-5" />
              <span className="text-gray-600">{user?.emailAddresses[0].emailAddress}</span>
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center space-x-3">
              <FaUser className="text-gray-400 w-5 h-5" />
              <span className="text-gray-600">{user?.firstName} {user?.lastName}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}