'use client'

import {useUser } from "@clerk/nextjs"
import { FaEnvelope, FaUser, FaCrown, FaBell, FaHistory, FaCog } from "react-icons/fa"
import { useState } from "react"
import { motion } from "framer-motion"

export default function ProfilePage() {
  const { user, isLoaded } = useUser()
  const [showSubscribeModal, setShowSubscribeModal] = useState(false)

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

  const subscriptionTiers = [
    {
      name: 'Basic',
      price: '$9.99/mo',
      features: ['Basic Features', 'Email Support', 'Limited Access'],
      color: 'bg-blue-500'
    },
    {
      name: 'Pro',
      price: '$19.99/mo',
      features: ['All Basic Features', 'Priority Support', 'Full Access', 'Advanced Analytics'],
      color: 'bg-purple-500'
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-100 via-purple-50 to-pink-100 p-8">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-4xl mx-auto"
      >
        {/* Profile Header */}
        <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-lg p-8 mb-8 border border-purple-100">
          <div className="flex items-center space-x-4">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 text-transparent bg-clip-text">
                {user?.firstName} {user?.lastName}
              </h1>
              <p className="text-indigo-600 font-medium">Free Plan</p>
            </div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Left Column - User Info */}
          <div className="flex flex-col gap-8">
            <motion.div
              whileHover={{ scale: 1.02 }}
              className="bg-white/80 backdrop-blur-sm p-8 rounded-xl shadow-lg border border-blue-100 flex-1"
            >
              <h2 className="text-2xl font-semibold mb-6 text-indigo-700">Profile Information</h2>
              <div className="space-y-4">
                <div className="flex items-center space-x-3">
                  <FaEnvelope className="text-purple-500 w-5 h-5" />
                  <span className="text-gray-700">{user?.emailAddresses[0].emailAddress}</span>
                </div>
                <div className="flex items-center space-x-3">
                  <FaUser className="text-purple-500 w-5 h-5" />
                  <span className="text-gray-700">{user?.firstName} {user?.lastName}</span>
                </div>
              </div>
            </motion.div>

            <motion.div
              whileHover={{ scale: 1.02 }}
              className="bg-white/80 backdrop-blur-sm p-8 rounded-xl shadow-lg border border-pink-100 flex-1"
            >
              <h2 className="text-2xl font-semibold mb-6 text-indigo-700">Quick Actions</h2>
              <div className="grid grid-cols-2 gap-4">
                <motion.button 
                  whileHover={{ scale: 1.05, rotate: -2 }}
                  whileTap={{ scale: 0.95 }}
                  className="p-6 bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg flex flex-col items-center hover:from-purple-100 hover:to-pink-100 transition-colors shadow-sm"
                >
                  <FaHistory className="w-6 h-6 text-purple-600 mb-2" />
                  <span className="text-gray-700 font-medium">History</span>
                </motion.button>

                <motion.button 
                  whileHover={{ scale: 1.05, y: -5 }}
                  whileTap={{ scale: 0.95 }}
                  className="p-6 bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg flex flex-col items-center hover:from-blue-100 hover:to-purple-100 transition-colors shadow-sm"
                >
                  <FaBell className="w-6 h-6 text-indigo-600 mb-2" />
                  <span className="text-gray-700 font-medium">Notifications</span>
                </motion.button>

                <motion.button 
                  whileHover={{ scale: 1.05, rotate: 2 }}
                  whileTap={{ scale: 0.95 }}
                  className="p-6 bg-gradient-to-br from-indigo-50 to-blue-50 rounded-lg flex flex-col items-center hover:from-indigo-100 hover:to-blue-100 transition-colors shadow-sm"
                >
                  <FaCog className="w-6 h-6 text-blue-600 mb-2" />
                  <span className="text-gray-700 font-medium">Settings</span>
                </motion.button>

                <motion.button 
                  whileHover={{ 
                    scale: 1.05,
                    boxShadow: "0px 0px 8px rgb(219, 39, 119)"
                  }}
                  whileTap={{ scale: 0.95 }}
                  className="p-6 bg-gradient-to-br from-pink-50 to-rose-50 rounded-lg flex flex-col items-center hover:from-pink-100 hover:to-rose-100 transition-colors shadow-sm"
                >
                  <FaCrown className="w-6 h-6 text-pink-600 mb-2" />
                  <span className="text-gray-700 font-medium">Upgrade</span>
                </motion.button>
              </div>
            </motion.div>
          </div>

          {/* Right Column - Subscription Plans */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-white/80 backdrop-blur-sm p-8 rounded-xl shadow-lg border border-indigo-100 h-full"
          >
            <h2 className="text-2xl font-semibold mb-6 text-indigo-700">Subscription Plans</h2>
            <div className="space-y-6">
              {subscriptionTiers.map((tier, index) => (
                <motion.div
                  key={tier.name}
                  whileHover={{ scale: 1.02 }}
                  className="border border-purple-100 rounded-lg p-6 cursor-pointer hover:border-purple-300 transition-colors bg-gradient-to-br from-white to-purple-50"
                >
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="font-semibold text-xl text-purple-700">{tier.name}</h3>
                    <span className="font-bold text-xl text-indigo-600">{tier.price}</span>
                  </div>
                  <ul className="space-y-3">
                    {tier.features.map((feature, i) => (
                      <li key={i} className="text-gray-700 flex items-center">
                        <span className="mr-2 text-purple-500">•</span>
                        {feature}
                      </li>
                    ))}
                  </ul>
                  <button 
                    className={`mt-4 w-full py-3 px-4 rounded-lg text-white bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 transition-all shadow-md hover:shadow-lg`}
                    onClick={() => setShowSubscribeModal(true)}
                  >
                    Subscribe to {tier.name}
                  </button>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </motion.div>

      {/* Subscribe Modal */}
      {showSubscribeModal && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4"
        >
          <motion.div
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            className="bg-white/90 backdrop-blur-sm rounded-xl p-8 max-w-md w-full shadow-2xl border border-purple-100"
          >
            <h2 className="text-2xl font-bold mb-4 text-indigo-700">Subscribe</h2>
            <p className="text-gray-700 mb-6">
              Please contact our sales team to complete your subscription.
            </p>
            <button
              className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-3 rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all shadow-md hover:shadow-lg"
              onClick={() => setShowSubscribeModal(false)}
            >
              Close
            </button>
          </motion.div>
        </motion.div>
      )}
    </div>
  )
}