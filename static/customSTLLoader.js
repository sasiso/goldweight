
import {
  BufferAttribute,
  BufferGeometry,
  FileLoader,
  Float32BufferAttribute,
  Loader,
  Vector3,
} from './three.module.min.js';

class CustomSTLLoader extends Loader {
  constructor(manager) {
    super(manager);
  }

  parse(data) {
    const text = new TextDecoder().decode(data);

    const geometry = new BufferGeometry();
    const positions = [];
    const normals = [];

    // Parse the STL data from 'text' and populate 'positions' and 'normals' arrays
    // You'll need to implement your custom STL parsing logic here

    // Example parsing code:
    const lines = text.split('\n');
    for (const line of lines) {
      if (line.startsWith('vertex ')) {
        const parts = line.trim().split(/\s+/);
        if (parts.length === 4) {
          const x = parseFloat(parts[1]);
          const y = parseFloat(parts[2]);
          const z = parseFloat(parts[3]);
          positions.push(x, y, z);
        }
      } else if (line.startsWith('facet normal ')) {
        const parts = line.trim().split(/\s+/);
        if (parts.length === 5) {
          const nx = parseFloat(parts[2]);
          const ny = parseFloat(parts[3]);
          const nz = parseFloat(parts[4]);
          normals.push(nx, ny, nz);
        }
      }
    }

    geometry.setAttribute('position', new Float32BufferAttribute(positions, 3));
    geometry.setAttribute('normal', new Float32BufferAttribute(normals, 3));

    return geometry;
  }

  load(url, onLoad, onProgress, onError) {
    const scope = this;

    const loader = new FileLoader();
    loader.setPath(scope.path);
    loader.setResponseType('arraybuffer');
    loader.setRequestHeader(scope.requestHeader);
    loader.setWithCredentials(scope.withCredentials);

    loader.load(
      url,
      function (data) {
        try {
          const geometry = scope.parse(data);
          onLoad(geometry);
        } catch (e) {
          if (onError) {
            onError(e);
          } else {
            console.error(e);
          }
          scope.manager.itemError(url);
        }
      },
      onProgress,
      onError
    );
  }
}

export { CustomSTLLoader };
	