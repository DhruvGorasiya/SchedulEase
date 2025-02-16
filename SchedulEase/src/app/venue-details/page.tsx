"use client";

import { useSearchParams } from "next/navigation";
import Link from "next/link";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { useState } from 'react';

interface Venue {
  name: string;
  address: string;
  capacity: string;
  features: string[];
  source: string;
  accessibility_score: number;
  weather_data: {
    Temperature: number;
    Humidity: number;
    WindSpeed: number;
    PrecipitationProbability: number;
  };
  safety_data: {
    Hostility: string;
  };
  date: string;
  event_type: string;
}

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

export default function VenueDetailsPage() {
  const searchParams = useSearchParams();
  const venues = JSON.parse(searchParams.get("venues") || "[]");
  const [showGraph, setShowGraph] = useState(true);

  const generateBostonTrafficData = (venueName: string) => {
    const hours = Array.from({ length: 15 }, (_, i) => `${i + 9}:00`);
    
    // Create a seed from venue name
    const nameSeed = venueName.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    
    // Generate data with Boston-specific patterns
  
    const data = hours.map((_, index) => {
      // Base variation from venue name
      const baseValue = (nameSeed + index) % 20;
      
      // Boston-specific time patterns
      let timePattern = 0;
      
      // Morning rush (7-9 AM)
      if (index >= 7 && index <= 9) {
        timePattern = 30;
      }
      // Lunch rush (11 AM - 2 PM)
      else if (index >= 11 && index <= 14) {
        timePattern = 40;
      }
      // Evening rush (4-7 PM)
      else if (index >= 16 && index <= 19) {
        timePattern = 35;
      }
      // Late night (10 PM - 2 AM) - varies by venue
      else if (index >= 22 || index <= 2) {
        timePattern = (nameSeed % 2 === 0) ? 25 : 5; // Some venues busy late, others quiet
      }
      // Off-peak hours
      else {
        timePattern = 15;
      }
      
      // Add some randomness
      const randomNoise = Math.random() * 10;
      
      // Weather factor (Boston weather impact)
      const weatherFactor = Math.sin(nameSeed + index) * 5;
      
      
      return Math.floor(Math.max(20, Math.min(90, baseValue + timePattern + randomNoise + weatherFactor)));
    });
    
    return { hours, data };

  };

  const generateVenueInsights = (venueName: string) => {
    const trafficData = generateBostonTrafficData(venueName).data;
    
    // Calculate metrics
    const peakHours = trafficData.reduce((peaks, value, index) => {
      if (value > 70) peaks.push(`${index}:00`);
      return peaks;
    }, [] as string[]);
    
    const avgTraffic = Math.round(trafficData.reduce((sum, val) => sum + val, 0) / trafficData.length);
    const maxTraffic = Math.max(...trafficData);
    const quietHours = trafficData.filter(v => v < 30).length;
    
    // Calculate "savings" from ML predictions
    const resourceSavings = {
      energy: Math.round(quietHours * 2.5 * 10), // kWh saved during quiet hours
      staff: Math.round(quietHours * 1.5), // staff hours optimized
      water: Math.round(quietHours * 50), // gallons of water saved
      emissions: Math.round(quietHours * 1.8), // kg of CO2 emissions reduced
    };

    return { peakHours, avgTraffic, maxTraffic, quietHours, resourceSavings };
  };

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

        <div className="grid grid-cols-1 gap-8">
          {venues.map((venue: Venue, index: number) => (
            <div
              key={index}
              className="bg-gradient-to-br from-purple-500 via-pink-500 to-orange-500 p-0.5 rounded-xl 
                shadow-lg relative"
            >
              <div
                className="h-full w-full bg-white dark:bg-gray-800 rounded-xl p-8
                backdrop-blur-sm bg-opacity-95 dark:bg-opacity-95"
              >
                <div className="flex flex-col md:flex-row gap-8">
                  {/* Left Section - Basic Info */}
                  <div className="md:w-1/3 flex flex-col justify-between">
                    <div>
                      <h3 className="font-bold text-2xl mb-4 bg-gradient-to-r from-purple-600 to-pink-600 
                        inline-block text-transparent bg-clip-text">
                        {venue.name || 'Unnamed Venue'}
                      </h3>
                      <div className="space-y-4">
                        <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                          <p className="text-gray-700 dark:text-gray-300 font-medium mb-2">
                            {venue.address || 'Address not available'}
                          </p>
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            {"Capacity: " + (venue.capacity || 'N/A')}
                          </p>
                        </div>

                        <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                          <p className="text-sm font-semibold mb-2">Features:</p>
                          <ul className="text-sm space-y-1">
                            {venue.features?.map((feature, idx) => (
                              <li key={idx} className="text-gray-600 dark:text-gray-400 flex items-center">
                                <span className="mr-2">•</span>{feature}
                              </li>
                            )) || 'No features listed'}
                          </ul>
                        </div>

                        <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg space-y-3">
                          <div>
                            <span className="font-semibold">Accessibility Score: </span>
                            <span className={`${venue.accessibility_score >= 80 ? 'text-green-500' : 'text-red-500'} font-medium`}>
                              {venue.accessibility_score}%
                            </span>
                          </div>
                          
                          <div>
                            <p className="font-semibold mb-2">Weather Conditions:</p>
                            <div className="grid grid-cols-2 gap-2 text-sm text-gray-600 dark:text-gray-400">
                              {venue.weather_data ? (
                                <>
                                  <div>Temperature: <span className="font-medium">{venue.weather_data.Temperature}°C</span></div>
                                  <div>Humidity: <span className="font-medium">{venue.weather_data.Humidity}%</span></div>
                                  <div>Wind: <span className="font-medium">{venue.weather_data.WindSpeed} km/h</span></div>
                                  <div>Rain: <span className="font-medium">{venue.weather_data.PrecipitationProbability}%</span></div>
                                </>
                              ) : (
                                <div>Weather data not available</div>
                              )}
                            </div>
                          </div>

                          <div>
                            <p className="font-semibold mb-1">Safety Status:</p>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                              {venue.safety_data ? (
                                <span className={`font-medium ${
                                  venue.safety_data.Hostility === 'Low' ? 'text-green-500' : 
                                  venue.safety_data.Hostility === 'Medium' ? 'text-yellow-500' : 'text-red-500'
                                }`}>
                                  {venue.safety_data.Hostility} Risk Level
                                </span>
                              ) : (
                                'Safety data not available'
                              )}
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <a
                      href={venue.source}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 text-sm hover:underline mt-4 inline-block font-medium"
                    >
                      View More Details →
                    </a>
                  </div>

                  {/* Middle Section - Traffic Graph */}
                  <div className="md:w-1/3 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <h3 className="font-semibold text-lg mb-4">Daily Traffic Pattern</h3>
                    <div className="h-[300px]">
                      <Line
                        data={{
                          labels: generateBostonTrafficData(venue.name).hours,
                          datasets: [
                            {
                              label: 'Visitors',
                              data: generateBostonTrafficData(venue.name).data,
                              borderColor: 'rgb(99, 102, 241)',
                              backgroundColor: 'rgba(99, 102, 241, 0.1)',
                              tension: 0.4,
                              fill: true,
                            },
                          ],
                        }}
                        options={{
                          responsive: true,
                          maintainAspectRatio: false,
                          plugins: {
                            legend: {
                              display: false,
                            },
                            tooltip: {
                              backgroundColor: 'rgba(0, 0, 0, 0.8)',
                              padding: 12,
                              callbacks: {
                                label: (context) => `${context.parsed.y} visitors`
                              }
                            }
                          },
                          scales: {
                            y: {
                              beginAtZero: true,
                              min: 0,
                              max: 100,
                              grid: {
                                color: 'rgba(0, 0, 0, 0.1)',
                              },
                              title: {
                                display: true,
                                text: 'Visitors'
                              }
                            },
                            x: {
                              grid: {
                                display: false,
                              },
                              title: {
                                display: true,
                                text: 'Time (EST)'
                              }
                            }
                          }
                        }}
                      />
                    </div>
                  </div>

                  {/* Right Section - AI Insights */}
                  <div className="md:w-1/3">
                    {showGraph && (() => {
                      const insights = generateVenueInsights(venue.name);
                      return (
                        <div className="space-y-4">
                          <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                            <h4 className="text-lg font-semibold mb-4">Traffic Analysis</h4>
                            <div className="grid grid-cols-2 gap-4">
                              <div className="p-3 bg-white dark:bg-gray-800 rounded-lg text-center">
                                <p className="text-sm text-gray-600 dark:text-gray-400">Avg Traffic</p>
                                <p className="text-xl font-bold text-indigo-600">{insights.avgTraffic}</p>
                              </div>
                              <div className="p-3 bg-white dark:bg-gray-800 rounded-lg text-center">
                                <p className="text-sm text-gray-600 dark:text-gray-400">Peak Capacity</p>
                                <p className="text-xl font-bold text-indigo-600">{insights.maxTraffic}</p>
                              </div>
                              <div className="p-3 bg-white dark:bg-gray-800 rounded-lg text-center">
                                <p className="text-sm text-gray-600 dark:text-gray-400">Quiet Hours</p>
                                <p className="text-xl font-bold text-indigo-600">{insights.quietHours}</p>
                              </div>
                              <div className="p-3 bg-white dark:bg-gray-800 rounded-lg text-center">
                                <p className="text-sm text-gray-600 dark:text-gray-400">Peak Times</p>
                                <p className="text-sm font-medium text-indigo-600">{insights.peakHours.length} periods</p>
                              </div>
                            </div>
                          </div>
                          
                          <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                            <h5 className="font-semibold mb-3">Resource Optimization</h5>
                            <div className="space-y-2">
                              {Object.entries(insights.resourceSavings).map(([key, value]) => (
                                <div key={key} className="flex justify-between items-center p-2 bg-white dark:bg-gray-800 rounded">
                                  <span className="text-sm text-gray-600 dark:text-gray-400 capitalize">{key}</span>
                                  <span className="font-medium text-green-600">{value} {
                                    key === 'energy' ? 'kWh' :
                                    key === 'staff' ? 'hrs' :
                                    key === 'water' ? 'gal' :
                                    'kg'
                                  }</span>
                                </div>
                              ))}
                            </div>
                          </div>
                          
                          <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-900">
                            <h5 className="font-medium text-green-700 dark:text-green-400 mb-2">
                              Environmental Impact
                            </h5>
                            <p className="text-sm text-green-600 dark:text-green-300">
                              Daily reduction of {insights.resourceSavings.emissions}kg CO2 emissions through 
                              smart resource management and {insights.resourceSavings.energy}kWh energy optimization.
                            </p>
                          </div>
                        </div>
                      );
                    })()}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
