import React, { useState, useEffect } from 'react';
import { Card, CardContent } from "./ui/card";

const codeSnippets = [
  {
    language: 'JavaScript',
    code: `// AI Code Review Suggestion
function optimizePerformance(data) {
  // ✅ Optimized with memoization
  return useMemo(() => 
    data.filter(item => item.active)
  , [data]);
}`
  },
  {
    language: 'Python',
    code: `# Bug Detection & Fix
def calculate_average(numbers):
    # 🐛 Fixed: Handle empty list
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)`
  },
  {
    language: 'TypeScript',
    code: `// Auto-generated Test Case
describe('UserService', () => {
  it('should handle edge cases', () => {
    // ✅ 100% coverage achieved
    expect(service.getUser('')).toThrow();
  });
});`
  }
];

const CodeAnimation = () => {
  const [currentSnippet, setCurrentSnippet] = useState(0);
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    const interval = setInterval(() => {
      setIsVisible(false);
      setTimeout(() => {
        setCurrentSnippet((prev) => (prev + 1) % codeSnippets.length);
        setIsVisible(true);
      }, 300);
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  return (
    <Card className="max-w-2xl mx-auto bg-black/60 backdrop-blur-sm border border-gray-700">
      <CardContent className="p-6">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-3 h-3 rounded-full bg-red-500"></div>
          <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
          <div className="w-3 h-3 rounded-full bg-green-500"></div>
          <span className="ml-4 text-sm text-gray-400">
            {codeSnippets[currentSnippet].language}
          </span>
        </div>
        <div 
          className={`transition-all duration-300 ${
            isVisible ? 'opacity-100 transform translate-y-0' : 'opacity-0 transform translate-y-2'
          }`}
        >
          <pre className="text-left text-sm text-gray-300 font-mono leading-relaxed overflow-x-auto">
            <code>{codeSnippets[currentSnippet].code}</code>
          </pre>
        </div>
      </CardContent>
    </Card>
  );
};

export default CodeAnimation;
