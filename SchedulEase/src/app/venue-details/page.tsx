"use client";

import { useSearchParams } from 'next/navigation';
import Link from 'next/link';

interface Venue {
  name: string;
  address: string;
  capacity: string;
  features: string[];
  source: string;
}

export default function VenueDetailsPage() {
  const searchParams = useSearchParams();
  const venues = JSON.parse(searchParams.get('venues') || '[]');

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-2xl font-semibold text-gray-800 dark:text-white">
            Venue Recommendations
          </h1>
          <Link 
            href="/chat"
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Back to Chat
          </Link>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {venues.map((venue: Venue, index: number) => (
            <div 
              key={index} 
              className="bg-gradient-to-br from-purple-500 via-pink-500 to-orange-500 p-0.5 rounded-lg 
                transform transition-all duration-300 hover:scale-105 hover:shadow-xl 
                relative group animate-gradient-xy"
            >
              <div className="h-full w-full bg-white dark:bg-gray-800 rounded-lg p-6 
                backdrop-blur-sm bg-opacity-95 dark:bg-opacity-95
                before:absolute before:inset-0 before:bg-texture before:opacity-5 before:mix-blend-overlay">
                {/* Tooltip with venue data */}
                <div className="fixed inset-0 invisible group-hover:visible opacity-0 group-hover:opacity-100 
                  transition-all duration-300 flex items-center justify-center bg-black bg-opacity-50 z-50">
                  <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-xl max-w-md w-full 
                    transform scale-95 group-hover:scale-100 transition-all duration-300">
                    <h4 className="text-2xl font-bold text-black mb-4">{venue.name}</h4>
                    <div className="space-y-4">
                      <div>
                        <p className="text-black font-medium">Address:</p>
                        <p className="text-black">{venue.address}</p>
                      </div>
                      <div>
                        <p className="text-black font-medium">Capacity:</p>
                        <p className="text-black">{venue.capacity}</p>
                      </div>
                      <div>
                        <p className="text-black font-medium mb-2">Features:</p>
                        <ul className="list-disc list-inside">
                          {venue.features.map((feature, idx) => (
                            <li key={idx} className="text-black">{feature}</li>
                          ))}
                        </ul>
                      </div>
                      {venue.source && (
                        <a 
                          href={venue.source}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-block mt-4 text-blue-600 hover:underline"
                        >
                          More Info
                        </a>
                      )}
                    </div>
                  </div>
                </div>

                <h3 className="font-semibold text-xl mb-2 bg-gradient-to-r from-purple-600 to-pink-600 
                  inline-block text-transparent bg-clip-text">{venue.name}</h3>
                <p className="text-gray-600 dark:text-gray-400 mb-2">{venue.address}</p>
                <p className="text-sm mb-4">{`Capacity: ${venue.capacity}`}</p>
                <div className="mb-4">
                  <p className="text-sm font-semibold mb-2">Features:</p>
                  <ul className="text-sm list-disc list-inside">
                    {venue.features.map((feature, idx) => (
                      <li key={idx} className="text-gray-600 dark:text-gray-400">
                        {feature}
                      </li>
                    ))}
                  </ul>
                </div>
                <a 
                  href={venue.source}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 text-sm hover:underline"
                >
                  More Info
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
