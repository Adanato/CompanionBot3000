import React, { useRef, useEffect } from 'react';
import { useLoader, useFrame } from '@react-three/fiber';
import { FBXLoader } from 'three-stdlib';
import * as THREE from 'three';

function BotModel({ isSpeaking }) {
  const modelRef = useRef();
  const mixerRef = useRef();
  const clockRef = useRef(new THREE.Clock());

  // Load the FBX model
  const fbx = useLoader(FBXLoader, '/Emi.fbx');

  useEffect(() => {
    if (fbx.animations && fbx.animations.length > 0) {
      mixerRef.current = new THREE.AnimationMixer(fbx);
      const action = mixerRef.current.clipAction(fbx.animations[0]);
      action.play();
      action.paused = true; // Start paused
    } else {
      console.warn('No animations found in the FBX model.');
    }
  }, [fbx]);

  useEffect(() => {
    if (mixerRef.current) {
      const action = mixerRef.current.existingAction(fbx.animations[0]);
      if (action) {
        action.paused = !isSpeaking; // Play or pause based on speaking
      }
    }
  }, [isSpeaking, fbx]);

  useFrame(() => {
    if (mixerRef.current) {
      const delta = clockRef.current.getDelta();
      mixerRef.current.update(delta);
    }
  });

  return (
    fbx ? (
      <primitive
        ref={modelRef}
        object={fbx}
        position={[0, -3, 0]} // Move model upwards (adjust Y-axis if needed)
        scale={[0.2, 0.2, 0.2]} // Reduce size
      />
    ) : null
  );
}

export default BotModel;
