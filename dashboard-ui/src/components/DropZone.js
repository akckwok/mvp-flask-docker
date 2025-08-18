export function createDropZone(container, onFileSelect) {
    container.innerHTML = `
        <div class="drop-zone">
            <p>Drag & Drop a file here or click to select</p>
            <input type="file" class="drop-zone-input" style="display: none;">
        </div>
        <div class="file-info"></div>
    `;

    const dropZone = container.querySelector('.drop-zone');
    const fileInput = container.querySelector('.drop-zone-input');
    const fileInfo = container.querySelector('.file-info');

    const handleClick = () => fileInput.click();
    const handleFileChange = () => {
        if (fileInput.files.length > 0) {
            handleFile(fileInput.files[0]);
        }
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        dropZone.classList.add('hover');
    };

    const handleDragLeave = () => {
        dropZone.classList.remove('hover');
    };

    const handleDrop = (e) => {
        e.preventDefault();
        dropZone.classList.remove('hover');
        const file = e.dataTransfer.files[0];
        if (file) {
            handleFile(file);
        }
    };

    function handleFile(file) {
        fileInfo.innerHTML = `Selected file: <strong>${file.name}</strong> (${(file.size / 1024).toFixed(2)} KB)`;
        if (onFileSelect) {
            onFileSelect(file);
        }
    }

    dropZone.addEventListener('click', handleClick);
    fileInput.addEventListener('change', handleFileChange);
    dropZone.addEventListener('dragover', handleDragOver);
    dropZone.addEventListener('dragleave', handleDragLeave);
    dropZone.addEventListener('drop', handleDrop);

    // Add styling
    const style = document.createElement('style');
    style.textContent = `
        .drop-zone {
            border: 2px dashed #ccc;
            border-radius: 8px;
            padding: 40px;
            text-align: center;
            cursor: pointer;
            transition: background-color 0.2s, border-color 0.2s;
            background-color: #fafafa;
        }
        .drop-zone.hover {
            background-color: #eef8ff;
            border-color: #007bff;
        }
        .file-info {
            margin-top: 20px;
            font-size: 1rem;
        }
    `;
    container.appendChild(style);
}
