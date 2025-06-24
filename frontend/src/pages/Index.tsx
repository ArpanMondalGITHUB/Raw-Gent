import { useState, useEffect, startTransition, useTransition } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import Hero3DScene from '../components/Hero3DScene';
import CodeAnimation from '../components/CodeAnimation';
import FeatureCards from '../components/FeatureCards';
import { Button } from '../components/ui/button';
import { loginWithGitHub } from "../services/auth";


const Index = () => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [loading, setLoading] = useState(false);
  const[pending , startTransition] = useTransition()
  const handleLogin = () =>{
    startTransition( ()=>{
      new Promise(res=>setTimeout(res,5000))
    })

    loginWithGitHub()
    
  }

  useEffect(() => {
    setIsLoaded(true);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white overflow-hidden">
      {/* Navigation */}
      <nav className="relative z-50 p-6 flex justify-between items-center">
        <div className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
          Raw-Gent AI
        </div>
        <Button variant="outline" disabled={pending} onClick={handleLogin} className="border-cyan-400 text-cyan-400 hover:bg-cyan-400 hover:text-black transition-all duration-300">
          Get Started
        </Button>
      </nav>

      {/* Hero Section */}
      <div className="relative min-h-screen flex items-center justify-center">
        {/* 3D Background */}
        <div className="absolute inset-0 w-full h-full">
          <Canvas camera={{ position: [0, 0, 5], fov: 75 }}>
            <Hero3DScene />
            <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={0.5} />
          </Canvas>
        </div>

        {/* Hero Content */}
        <div className={`relative z-10 text-center max-w-4xl mx-auto px-6 transition-all duration-1000 ${isLoaded ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
          <h1 className="text-6xl md:text-8xl font-bold mb-8 bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent animate-pulse">
            AI Code Agent
          </h1>
          <p className="text-xl md:text-2xl mb-8 text-gray-300 max-w-2xl mx-auto leading-relaxed">
            Your intelligent coding companion that reviews, builds, tests, and debugs your code with superhuman precision
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <Button size="lg" className="bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-600 hover:to-purple-600 text-white font-semibold px-8 py-4 rounded-full transition-all duration-300 transform hover:scale-105">
              Start Coding
            </Button>
            <Button size="lg" variant="outline" className="border-2 border-cyan-400 text-cyan-400 hover:bg-cyan-400 hover:text-black font-semibold px-8 py-4 rounded-full transition-all duration-300">
              Watch Demo
            </Button>
          </div>

          {/* Animated Code Preview */}
          <CodeAnimation />
        </div>
      </div>

      {/* Features Section */}
      <div className="relative z-10 py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-4xl md:text-5xl font-bold text-center mb-16 bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
            Superhuman Coding Powers
          </h2>
          <FeatureCards />
        </div>
      </div>

      {/* Stats Section */}
      <div className="relative z-10 py-20 px-6 bg-black/20 backdrop-blur-sm">
        <div className="max-w-4xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div className="space-y-2">
              <div className="text-3xl md:text-4xl font-bold text-cyan-400">99.9%</div>
              <div className="text-gray-400">Bug Detection</div>
            </div>
            <div className="space-y-2">
              <div className="text-3xl md:text-4xl font-bold text-purple-400">10x</div>
              <div className="text-gray-400">Faster Coding</div>
            </div>
            <div className="space-y-2">
              <div className="text-3xl md:text-4xl font-bold text-pink-400">100%</div>
              <div className="text-gray-400">Test Coverage</div>
            </div>
            <div className="space-y-2">
              <div className="text-3xl md:text-4xl font-bold text-cyan-400">24/7</div>
              <div className="text-gray-400">Code Review</div>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="relative z-10 py-20 px-6 text-center">
        <div className="max-w-2xl mx-auto">
          <h3 className="text-3xl md:text-4xl font-bold mb-6 bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
            Ready to Transform Your Code?
          </h3>
          <p className="text-xl text-gray-300 mb-8">
            Join thousands of developers who've supercharged their productivity
          </p>
          <Button size="lg" className="bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-600 hover:to-purple-600 text-white font-semibold px-12 py-4 rounded-full transition-all duration-300 transform hover:scale-105">
            Get Started Free
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Index;
