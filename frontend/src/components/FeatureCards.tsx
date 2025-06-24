import React from 'react';
import { Card, CardContent } from "./ui/card";
import { CheckCircle, Code, Bug, TestTube } from 'lucide-react';

const features = [
  {
    icon: CheckCircle,
    title: 'Smart Code Review',
    description: 'AI-powered analysis that catches issues humans miss. Get instant feedback on code quality, security vulnerabilities, and performance optimizations.',
    color: 'from-cyan-400 to-blue-500'
  },
  {
    icon: Code,
    title: 'Feature Development',
    description: 'Transform ideas into production-ready code. Our AI understands context and writes clean, maintainable features that integrate seamlessly.',
    color: 'from-purple-400 to-pink-500'
  },
  {
    icon: TestTube,
    title: 'Automated Testing',
    description: 'Generate comprehensive test suites automatically. Unit tests, integration tests, and edge cases - all covered with 100% accuracy.',
    color: 'from-green-400 to-cyan-500'
  },
  {
    icon: Bug,
    title: 'Bug Detection & Fix',
    description: 'Identify and resolve bugs before they reach production. Advanced pattern recognition finds even the most subtle issues.',
    color: 'from-orange-400 to-red-500'
  }
];

const FeatureCards = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {features.map((feature, index) => (
        <Card 
          key={index} 
          className="bg-black/40 backdrop-blur-sm border border-gray-700 hover:border-gray-500 transition-all duration-300 transform hover:scale-105 hover:rotate-1 group"
        >
          <CardContent className="p-6 text-center space-y-4">
            <div className={`w-16 h-16 mx-auto rounded-full bg-gradient-to-r ${feature.color} flex items-center justify-center group-hover:animate-pulse`}>
              <feature.icon className="w-8 h-8 text-white" />
            </div>
            <h3 className="text-xl font-bold text-white group-hover:text-transparent group-hover:bg-gradient-to-r group-hover:bg-clip-text group-hover:from-cyan-400 group-hover:to-purple-400 transition-all duration-300">
              {feature.title}
            </h3>
            <p className="text-gray-400 text-sm leading-relaxed group-hover:text-gray-300 transition-colors duration-300">
              {feature.description}
            </p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

export default FeatureCards;
