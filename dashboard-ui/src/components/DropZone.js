export function createDropZone(container, onFilesSelect) {
    container.innerHTML = `
        <div class="drop-zone border-2 border-dashed border-base-300 rounded-lg p-10 text-center cursor-pointer transition-colors duration-200 bg-base-200 hover:bg-base-300 hover:border-primary">
            <p>Drag & Drop files here or click to select</p>
            <input type="file" class="drop-zone-input hidden" multiple>
        </div>
        <div class="file-info mt-4 text-base"></div>
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
        dropZone.classList.add('bg-base-300', 'border-primary');
    };

    const handleDragLeave = () => {
        dropZone.classList.remove('bg-base-300', 'border-primary');
    };

    const handleDrop = (e) => {
        e.preventDefault();
        if (dropZone.classList.contains('disabled')) return;
        dropZone.classList.remove('bg-base-300', 'border-primary');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFiles(files);
        }
    };

    function handleFiles(files) {
        const fileList = Array.from(files);
        if (fileList.length === 1) {
            const file = fileList[0];
            fileInfo.innerHTML = `Selected file: <strong class="font-bold">${file.name}</strong> (${(file.size / 1024).toFixed(2)} KB)`;
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
}
