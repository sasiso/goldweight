import * as THREE from './three.module.min.js';
import { OrbitControls } from'./OrbitControls.js';
import { STLLoader } from './STLLoader.js';

let container;
let camera, cameraTarget, scene, renderer, controls;

function getVolume(geometry) {
	let position = geometry.attributes.position;
	let faces = position.count / 3;
	let sum = 0;
	let p1 = new THREE.Vector3(),
		p2 = new THREE.Vector3(),
		p3 = new THREE.Vector3();
	for (let i = 0; i < faces; i++) {
		p1.fromBufferAttribute(position, i * 3 + 0);
		p2.fromBufferAttribute(position, i * 3 + 1);
		p3.fromBufferAttribute(position, i * 3 + 2);
		sum += signedVolumeOfTriangle(p1, p2, p3);
	}
	return sum;
}

function signedVolumeOfTriangle(p1, p2, p3) {
	return p1.dot(p2.cross(p3)) / 6.0;
}

// Function to calculate gold weight in milligrams
function calculateGoldWeight(geometry) {
	// Use the model's dimensions to calculate gold weights for different karats
	const volumeInCubicCentimeters = getVolume(geometry);
	console.log("computed volume of a hollow cylinder: ", volumeInCubicCentimeters);

	// Define densities for different karats and silver in g/cm³
	const densities = {
		'9K': 11.0,
		'14K': 13.0,
		'18K': 15.6,
		'22K': 17.5,
		'24K': 19.6, // Adjusted density for 24K gold (higher than 22K)
		'925': 10.49  // Silver 925
	};

	const weights = {};

	// Calculate the weight in milligrams for each karat
	for (const karat in densities) {
		const density = densities[karat];
		const weightInMilligrams = (volumeInCubicCentimeters * density) / 1000.0; // Convert to milligrams
		weights[karat] = weightInMilligrams.toFixed(3);
	}

	return weights;
}

// Function to update the weight display table
function updateWeightDisplay(weights) {
	const weightDisplay = document.getElementById('weight-display');
	weightDisplay.innerHTML = ''; // Clear previous content

	// Create and populate the weight table
	const table = document.createElement('table');
	table.border = '1';
	table.innerHTML = `
                <thead>
                    <tr>
                        <th>Karat</th>
                        <th>Gold Weight (grams)</th>
                    </tr>
                </thead>
                <tbody>
                    ${Object.keys(weights)
			.map(karat => `<tr><td>${karat}</td><td>${weights[karat]}</td></tr>`)
			.join('')}
                </tbody>
            `;

	weightDisplay.appendChild(table);
}

function init() {
	container = document.createElement('div');
	document.body.appendChild(container);
    const w = window.innerHeight 
    const h = window.innerHeight 

	camera = new THREE.PerspectiveCamera(35,w / h, 1, 15);
	camera.position.set(3, 0.15, 3);

	cameraTarget = new THREE.Vector3(0, -0.25, 0);

	scene = new THREE.Scene();
	scene.background = new THREE.Color(0);	


	scene.add(new THREE.HemisphereLight(0x8d7c7c, 0x494966, 3));
	addShadowedLight(1, 1, 1, 0xffffff, 3.5);
	addShadowedLight(0.5, 1, -1, 0xffd500, 3);

	// Add OrbitControls for mouse interaction
	controls = new OrbitControls(camera, container);
	controls.target.set(0, 0, 0);
	controls.update();

	// renderer
	renderer = new THREE.WebGLRenderer({ antialias: true });
	renderer.setPixelRatio(window.devicePixelRatio);
	renderer.setSize(w, h);
	renderer.shadowMap.enabled = true;
	container.appendChild(renderer.domElement);

	window.addEventListener('resize', onWindowResize);
}

function clearScene() {
	// Remove only mesh objects from the scene
	scene.children.forEach((child) => {
		if (child instanceof THREE.Mesh) {
			scene.remove(child);
		}
	});
}

function addShadowedLight(x, y, z, color, intensity) {
	const directionalLight = new THREE.DirectionalLight(color, intensity);
	directionalLight.position.set(x, y, z);
	scene.add(directionalLight);

	directionalLight.castShadow = true;

	const d = 1;
	directionalLight.shadow.camera.left = -d;
	directionalLight.shadow.camera.right = d;
	directionalLight.shadow.camera.top = d;
	directionalLight.shadow.camera.bottom = -d;

	directionalLight.shadow.camera.near = 1;
	directionalLight.shadow.camera.far = 4;

	directionalLight.shadow.bias = -0.002;
}

function onWindowResize() {
	camera.aspect = window.innerWidth / window.innerHeight;
	camera.updateProjectionMatrix();
	renderer.setSize(window.innerWidth/1.5, window.innerHeight/1.5);
}

function animate() {
	requestAnimationFrame(animate);
	render();
}

function render() {
	renderer.render(scene, camera);
}
export function setup()
{
    init();
    animate();
    listen_events();

}
function listen_events() {
	const stlFileInput = document.getElementById('stl-file');
	const stlContainer = document.getElementById('stl-container');

	stlFileInput.addEventListener('change', function () {
		const file = stlFileInput.files[0];
		if (file) {
			// Clear the existing objects from the scene
			clearScene();

			const loader = new STLLoader();
			loader.load(URL.createObjectURL(file), function (geometry) {
				const material = new THREE.MeshPhongMaterial({
					color: 0xff9c7c,
					specular: 0x494949,
					shininess: 200
				});

				const mesh = new THREE.Mesh(geometry, material);

				// Calculate the bounding box of the loaded geometry
				const boundingBox = new THREE.Box3().setFromObject(mesh);

				// Calculate the object's size based on the bounding box
				const objectSize = new THREE.Vector3();

				boundingBox.getSize(objectSize);
				console.log("Object size is:", objectSize);

				// Define a minimum size threshold (adjust as needed)
				const minSizeThreshold = new THREE.Vector3(0.5, 0.5, 0.5);

				// Calculate the scale factor needed to meet the minimum size threshold
				const scaleFactor = new THREE.Vector3(0.02, 0.02, 0.02);
				// Apply the scale factor to the object
				mesh.scale.multiply(scaleFactor);
				console.log("scaleFactor is:", scaleFactor);

				// Customize position (if needed)
				mesh.position.set(0, 0, 0);
				mesh.rotation.set(-Math.PI / 2, 0, 0);

				mesh.castShadow = true;
				mesh.receiveShadow = true;

				scene.add(mesh);

				// Calculate gold weights and display them
				const weights = calculateGoldWeight(geometry);
				updateWeightDisplay(weights);
			});
		}
	});
}
