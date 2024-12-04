import React, { useRef, useEffect, useState } from 'react';
import { useLoader, useFrame } from '@react-three/fiber';
import { FBXLoader } from 'three-stdlib';
import * as THREE from 'three';

function BotModel({ isSpeaking }) {
  const mixerRef = useRef();
  const clockRef = useRef(new THREE.Clock());
  const [currentModel, setCurrentModel] = useState(null);
  const [animationFinished, setAnimationFinished] = useState(true); // Track when an animation is done
  const [speakingIndex, setSpeakingIndex] = useState(0);

  // Load models
  const fbxIdle = useLoader(FBXLoader, '/Emi.fbx'); // Idle animation
  const fbxSpeaking2 = useLoader(FBXLoader, '/Emi2.fbx'); // Speaking model 1
  const fbxSpeaking3 = useLoader(FBXLoader, '/Emi3.fbx'); // Speaking model 2
  const fbxSpeaking4 = useLoader(FBXLoader, '/Emi4.fbx'); // Speaking model 3
  const speakingModels = [fbxSpeaking2, fbxSpeaking3, fbxSpeaking4];

  // Handle speaking and idle logic
  useEffect(() => {
    if (isSpeaking && animationFinished) {
      // Start next speaking animation if speaking and no animation is running
      setAnimationFinished(false);
      setCurrentModel(speakingModels[speakingIndex]);
      setSpeakingIndex((prevIndex) => (prevIndex + 1) % speakingModels.length); // Cycle through speaking models
    } else if (!isSpeaking && animationFinished) {
      // If not speaking, ensure idle animation plays
      setCurrentModel(fbxIdle);
    }
  }, [isSpeaking, animationFinished, speakingIndex, speakingModels, fbxIdle]);

  // Play animation when currentModel changes
  useEffect(() => {
    if (currentModel && currentModel.animations.length > 0) {
      // Initialize animation mixer
      mixerRef.current = new THREE.AnimationMixer(currentModel);
      const action = mixerRef.current.clipAction(currentModel.animations[0]);
      action.loop = THREE.LoopOnce; // Play the animation fully
      action.clampWhenFinished = true; // Hold on the last frame when finished
      action.play();

      // Listen for when the animation finishes
      action.getMixer().addEventListener('finished', () => {
        setAnimationFinished(true); // Mark animation as finished
      });
    }
  }, [currentModel]);

  // Update animation on each frame
  useFrame(() => {
    if (mixerRef.current) {
      const delta = clockRef.current.getDelta();
      mixerRef.current.update(delta);
    }
  });

  return (
    currentModel ? (
      <primitive
        object={currentModel}
        position={[0, -12, 0]} // Keep consistent position
        scale={[0.2, 0.2, 0.2]} // Keep consistent scale
      />
    ) : null
  );
}

export default BotModel;
