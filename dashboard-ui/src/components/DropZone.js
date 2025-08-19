export function createDropZone(container, onFilesSelect) {
    container.innerHTML = `
        <div class="drop-zone">
            <p>Drag & Drop files here or click to select</p>
            <input type="file" class="drop-zone-input" style="display: none;" multiple>
        </div>
        <div class="file-info"></div>
    `;

    const dropZone = container.querySelector('.drop-zone');
    const fileInput = container.querySelector('.drop-zone-input');
    const fileInfo = container.querySelector('.file-info');

    const handleClick = () => {
        if (dropZone.classList.contains('disabled')) return;
        fileInput.click();
    };

    const handleFilesChange = (e) => {
        const files = e.target.files;
        if (files.length > 0) {
            handleFiles(files);
        }
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        if (dropZone.classList.contains('disabled')) return;
        dropZone.classList.add('hover');
    };

    const handleDragLeave = () => {
        dropZone.classList.remove('hover');
    };

    const handleDrop = (e) => {
        e.preventDefault();
        if (dropZone.classList.contains('disabled')) return;
        dropZone.classList.remove('hover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFiles(files);
        }
    };

    function handleFiles(files) {
        const fileList = Array.from(files);
        if (fileList.length === 1) {
            const file = fileList[0];
            fileInfo.innerHTML = `Selected file: <strong>${file.name}</strong> (${(file.size / 1024).toFixed(2)} KB)`;
        } else {
            fileInfo.innerHTML = `Selected ${fileList.length} files.`;
        }

        if (onFilesSelect) {
            onFilesSelect(fileList);
        }
    }

    dropZone.addEventListener('click', handleClick);
    fileInput.addEventListener('change', handleFilesChange);
    dropZone.addEventListener('dragover', handleDragOver);
    dropZone.addEventListener('dragleave', handleDragLeave);
    dropZone.addEventListener('drop', handleDrop);

    if (!document.getElementById('drop-zone-styles')) {
        const style = document.createElement('style');
        style.id = 'drop-zone-styles';
        style.textContent = `
            .drop-zone {
                border: 2px dashed #ccc; border-radius: 8px; padding: 40px;
                text-align: center; cursor: pointer; transition: background-color 0.2s, border-color 0.2s;
                background-color: #fafafa;
            }
            .drop-zone.hover { background-color: #eef8ff; border-color: #007bff; }
            .drop-zone.disabled {
                background-color: #f0f0f0;
                border-color: #d0d0d0;
                cursor: not-allowed;
                color: #a0a0a0;
            }
            .file-info { margin-top: 20px; font-size: 1rem; }
        `;
        container.appendChild(style);
    }
}
