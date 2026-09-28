import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
// @ts-ignore
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
// @ts-ignore
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader';
import { Maximize2, RotateCcw, Box, Eye, EyeOff, Layers } from 'lucide-react';
import { CADProperties } from '../../types';

interface ThreeViewerProps {
  stlBase64?: string;
  cadProperties?: CADProperties;
  height?: number;
}

export const ThreeViewer: React.FC<ThreeViewerProps> = ({
  stlBase64,
  cadProperties,
  height = 480,
}) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const [wireframe, setWireframe] = useState(false);
  const [showGrid, setShowGrid] = useState(true);
  const [modelColor, setModelColor] = useState('#38bdf8');
  const [isLoading, setIsLoading] = useState(false);

  const sceneRef = useRef<THREE.Scene | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const meshRef = useRef<THREE.Mesh | null>(null);
  const controlsRef = useRef<any>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const gridRef = useRef<THREE.GridHelper | null>(null);

  useEffect(() => {
    if (!mountRef.current) return;

    const width = mountRef.current.clientWidth;
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x090d16);
    sceneRef.current = scene;

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 2000);
    cameraRef.current = camera;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    rendererRef.current = renderer;

    mountRef.current.innerHTML = '';
    mountRef.current.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controlsRef.current = controls;

    // Studio Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
    scene.add(ambientLight);

    const keyLight = new THREE.DirectionalLight(0xffffff, 0.9);
    keyLight.position.set(100, 200, 150);
    scene.add(keyLight);

    const fillLight = new THREE.DirectionalLight(0x38bdf8, 0.5);
    fillLight.position.set(-100, -50, -100);
    scene.add(fillLight);

    const rimLight = new THREE.DirectionalLight(0x818cf8, 0.4);
    rimLight.position.set(0, -100, 100);
    scene.add(rimLight);

    // Coordinate Grid
    const grid = new THREE.GridHelper(200, 20, 0x334155, 0x1e293b);
    grid.position.y = 0;
    scene.add(grid);
    gridRef.current = grid;

    let animationFrameId: number;
    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    };
    animate();

    const handleResize = () => {
      if (!mountRef.current || !rendererRef.current || !cameraRef.current) return;
      const w = mountRef.current.clientWidth;
      cameraRef.current.aspect = w / height;
      cameraRef.current.updateProjectionMatrix();
      rendererRef.current.setSize(w, height);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('resize', handleResize);
      renderer.dispose();
    };
  }, [height]);

  // Load / update geometry when stlBase64 changes
  useEffect(() => {
    if (!sceneRef.current || !stlBase64) return;
    setIsLoading(true);

    try {
      if (meshRef.current) {
        sceneRef.current.remove(meshRef.current);
        meshRef.current.geometry.dispose();
      }

      const binaryString = atob(stlBase64);
      const len = binaryString.length;
      const bytes = new Uint8Array(len);
      for (let i = 0; i < len; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }

      const loader = new STLLoader();
      const geometry = loader.parse(bytes.buffer);
      geometry.center();
      geometry.computeVertexNormals();

      const material = new THREE.MeshPhysicalMaterial({
        color: new THREE.Color(modelColor),
        metalness: 0.15,
        roughness: 0.35,
        clearcoat: 0.3,
        clearcoatRoughness: 0.1,
        wireframe: wireframe,
        side: THREE.DoubleSide,
      });

      const mesh = new THREE.Mesh(geometry, material);
      sceneRef.current.add(mesh);
      meshRef.current = mesh;

      // Adjust camera to frame model
      geometry.computeBoundingSphere();
      const radius = geometry.boundingSphere?.radius || 50;
      if (cameraRef.current && controlsRef.current) {
        cameraRef.current.position.set(radius * 1.8, radius * 1.4, radius * 2.2);
        cameraRef.current.lookAt(0, 0, 0);
        controlsRef.current.target.set(0, 0, 0);
      }
    } catch (err) {
      console.error('Failed to parse STL in ThreeViewer:', err);
    } finally {
      setIsLoading(false);
    }
  }, [stlBase64, modelColor, wireframe]);

  // Update material properties without reloading mesh
  useEffect(() => {
    if (meshRef.current) {
      const mat = meshRef.current.material as THREE.MeshPhysicalMaterial;
      mat.color.set(modelColor);
      mat.wireframe = wireframe;
      mat.needsUpdate = true;
    }
  }, [modelColor, wireframe]);

  // Grid toggle
  useEffect(() => {
    if (gridRef.current) {
      gridRef.current.visible = showGrid;
    }
  }, [showGrid]);

  const handleResetCamera = () => {
    if (meshRef.current && cameraRef.current && controlsRef.current) {
      meshRef.current.geometry.computeBoundingSphere();
      const radius = meshRef.current.geometry.boundingSphere?.radius || 50;
      cameraRef.current.position.set(radius * 1.8, radius * 1.4, radius * 2.2);
      controlsRef.current.target.set(0, 0, 0);
      controlsRef.current.update();
    }
  };

  return (
    <div className="relative w-full rounded-xl overflow-hidden bg-slate-950 border border-slate-800 shadow-2xl">
      {/* 3D Viewport Controls Top Bar */}
      <div className="absolute top-3 left-3 right-3 flex justify-between items-center z-10 pointer-events-none">
        <div className="flex items-center gap-2 pointer-events-auto bg-slate-900/80 backdrop-blur-md px-3 py-1.5 rounded-lg border border-slate-700/60 text-xs text-slate-300">
          <Box className="w-3.5 h-3.5 text-sky-400" />
          <span className="font-semibold text-slate-200">
            {cadProperties?.device_type ? cadProperties.device_type.toUpperCase() : 'CAD VIEW'}
          </span>
          {cadProperties && (
            <span className="text-slate-400 font-mono">
              ({cadProperties.volume_mm3.toFixed(1)} mm³)
            </span>
          )}
        </div>

        <div className="flex items-center gap-1.5 pointer-events-auto bg-slate-900/80 backdrop-blur-md p-1 rounded-lg border border-slate-700/60">
          <button
            onClick={() => setWireframe(!wireframe)}
            title="Toggle Wireframe"
            className={`p-1.5 rounded text-xs transition-colors ${
              wireframe ? 'bg-sky-500 text-white' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Layers className="w-4 h-4" />
          </button>
          <button
            onClick={() => setShowGrid(!showGrid)}
            title="Toggle Coordinate Grid"
            className={`p-1.5 rounded text-xs transition-colors ${
              showGrid ? 'bg-slate-700 text-slate-200' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            {showGrid ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
          </button>
          <button
            onClick={handleResetCamera}
            title="Reset View"
            className="p-1.5 rounded text-xs text-slate-400 hover:text-slate-200 transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
          <input
            type="color"
            value={modelColor}
            onChange={(e) => setModelColor(e.target.value)}
            title="Model Shader Color"
            className="w-6 h-6 rounded cursor-pointer border-0 bg-transparent"
          />
        </div>
      </div>

      {/* Loading Overlay */}
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-slate-950/60 backdrop-blur-sm z-20">
          <div className="flex items-center gap-2 text-sky-400 text-sm font-medium">
            <div className="w-4 h-4 border-2 border-sky-400 border-t-transparent rounded-full animate-spin"></div>
            Regenerating Parametric Mesh...
          </div>
        </div>
      )}

      {/* Canvas container */}
      <div ref={mountRef} style={{ height }} className="w-full cursor-grab active:cursor-grabbing" />

      {/* Bottom overlay hints */}
      <div className="absolute bottom-2.5 left-3 text-[11px] text-slate-400 pointer-events-none bg-slate-900/60 px-2.5 py-1 rounded backdrop-blur">
        🖱️ Rotate: Left Drag | Pan: Right Drag | Zoom: Scroll Wheel
      </div>
    </div>
  );
};
