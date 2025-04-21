document.addEventListener("DOMContentLoaded", function() {
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);

  const canvas = document.getElementById("bgCanvas");
  const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setClearColor(0x111122, 1); // Darker, muted blue-gray for a medical feel

  // Generate simplified heartbeat waveform points
  function generateWaveformPoints() {
      const cyclePoints = [
          new THREE.Vector3(0, 0, 0),
          new THREE.Vector3(1, 0.3, 0),    // P wave
          new THREE.Vector3(1.5, -0.6, 0), // Q
          new THREE.Vector3(1.7, 1.2, 0),  // R (strong peak)
          new THREE.Vector3(1.9, -0.4, 0), // S
          new THREE.Vector3(3, 0.4, 0),    // T wave
          new THREE.Vector3(4, 0, 0)
      ];
      const points = [];
      const cycles = 3; // Fewer cycles for a cleaner look
      for (let i = 0; i < cycles; i++) {
          cyclePoints.forEach(p => {
              points.push(new THREE.Vector3(p.x + i * 4, p.y, p.z));
          });
      }
      return points;
  }

  const points = generateWaveformPoints();
  const curve = new THREE.CatmullRomCurve3(points);
  const tubeGeometry = new THREE.TubeGeometry(curve, 50, 0.3, 8, false); // Thinner tube

  const material = new THREE.MeshBasicMaterial({
      color: 0xff4444, // Soft red for heart association
      transparent: true,
      opacity: 0.4,
      blending: THREE.AdditiveBlending
  });

  const waveform = new THREE.Mesh(tubeGeometry, material);

  // Create a simpler grid with fewer lines, more spaced out
  const lines = [];
  const gridSize = 1; // Reduced density
  const spacing = 30; // More spacing for clarity
  const layers = 2;   // Fewer layers to avoid clutter
  for (let k = 0; k < layers; k++) {
      const z = -30 * (k + 1);
      for (let i = -gridSize; i <= gridSize; i++) {
          for (let j = -gridSize; j <= gridSize; j++) {
              const line = waveform.clone();
              line.position.set(i * spacing, j * spacing, z);
              scene.add(line);
              lines.push(line);
          }
      }
  }

  camera.position.set(20, 20, 80); // Closer view for focus
  camera.lookAt(0, 0, 0);

  window.addEventListener('resize', () => {
      renderer.setSize(window.innerWidth, window.innerHeight);
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
  });

  function animate() {
      requestAnimationFrame(animate);
      const time = Date.now() * 0.001;
      const pulse = (Math.sin(time * 2 * Math.PI * 0.67) + 1) / 2; // ~90 BPM heartbeat
      const opacity = 0.2 + pulse * 0.3; // Subtle pulse from 0.2 to 0.5
      lines.forEach(line => {
          line.material.opacity = opacity;
      });
      renderer.render(scene, camera);
  }
  animate();
});