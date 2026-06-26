import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.164/build/three.module.js";

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);

const camera = new THREE.PerspectiveCamera(
75,
window.innerWidth/window.innerHeight,
0.1,
1000
);

const renderer = new THREE.WebGLRenderer({
antialias:true
});

renderer.setSize(window.innerWidth,window.innerHeight);

document.body.appendChild(renderer.domElement);

// Lighting

const ambient = new THREE.AmbientLight(0xffffff,0.7);
scene.add(ambient);

const sun = new THREE.DirectionalLight(0xffffff,1);

sun.position.set(20,30,10);

scene.add(sun);

// Ground

const ground = new THREE.Mesh(
new THREE.PlaneGeometry(300,300),
new THREE.MeshStandardMaterial({
color:0x228822
})
);

ground.rotation.x=-Math.PI/2;

scene.add(ground);

// Clock

const clock=new THREE.Clock();

// Animation

function animate(){

requestAnimationFrame(animate);

renderer.render(scene,camera);

}

animate();
