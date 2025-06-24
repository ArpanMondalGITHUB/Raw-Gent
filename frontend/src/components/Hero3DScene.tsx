import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

const Hero3DScene = () => {
  const groupRef = useRef<THREE.Group>(null);
  
  // Create particle system for background stars
  const particles = useMemo(() => {
    const temp = [];
    for (let i = 0; i < 200; i++) {
      temp.push({
        position: [
          (Math.random() - 0.5) * 20,
          (Math.random() - 0.5) * 20,
          (Math.random() - 0.5) * 20
        ] as [number, number, number],
        scale: Math.random() * 0.5 + 0.1
      });
    }
    return temp;
  }, []);

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = state.clock.elapsedTime * 0.1;
      groupRef.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.1) * 0.1;
    }
  });

  return (
    <>
      {/* Ambient lighting */}
      <ambientLight intensity={0.2} />
      <pointLight position={[10, 10, 10]} intensity={1} color="#00ffff" />
      <pointLight position={[-10, -10, -10]} intensity={0.5} color="#ff00ff" />

      {/* Background particles */}
      {particles.map((particle, i) => (
        <mesh key={i} position={particle.position}>
          <sphereGeometry args={[0.02, 8, 8]} />
          <meshBasicMaterial color="#ffffff" transparent opacity={0.6} />
        </mesh>
      ))}

      {/* Main geometric shapes */}
      <group ref={groupRef}>
        {/* Floating Octahedron */}
        <mesh position={[-3, 2, 0]} rotation={[0, 0, Math.PI / 4]}>
          <octahedronGeometry args={[1]} />
          <meshStandardMaterial 
            color="#00ffff" 
            emissive="#003333" 
            transparent
            opacity={0.8}
          />
        </mesh>

        {/* Floating Box */}
        <mesh position={[3, -1, -2]} rotation={[Math.PI / 4, Math.PI / 4, 0]}>
          <boxGeometry args={[1.5, 1.5, 1.5]} />
          <meshStandardMaterial 
            color="#ff00ff" 
            emissive="#330033"
            transparent
            opacity={0.7}
          />
        </mesh>

        {/* Floating Torus */}
        <mesh position={[0, -2, 1]} rotation={[Math.PI / 2, 0, 0]}>
          <torusGeometry args={[1, 0.3, 16, 32]} />
          <meshStandardMaterial 
            color="#ffff00" 
            emissive="#333300"
            transparent
            opacity={0.6}
          />
        </mesh>

        {/* Floating Sphere */}
        <mesh position={[-1, 3, 2]}>
          <sphereGeometry args={[0.8, 32, 32]} />
          <meshStandardMaterial 
            color="#00ff00" 
            emissive="#003300"
            transparent
            opacity={0.8}
          />
        </mesh>

        {/* Wireframe Octahedron for extra depth */}
        <mesh position={[2, 1, 3]} rotation={[Math.PI / 3, Math.PI / 3, 0]}>
          <octahedronGeometry args={[1.2]} />
          <meshBasicMaterial color="#ffffff" wireframe transparent opacity={0.3} />
        </mesh>
      </group>
    </>
  );
};

export default Hero3DScene;
