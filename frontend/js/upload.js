
// Lấy các thành phần trên giao diện
const imageInput = document.getElementById("imageInput");
const imagePreview = document.getElementById("imagePreview");
const uploadStatus = document.getElementById("uploadStatus");
const dropArea = document.getElementById("dropArea");
const clearButton = document.getElementById("clearButton");

// Dung lượng ảnh tối đa: 5MB
const MAX_FILE_SIZE = 5 * 1024 * 1024;

// Lưu địa chỉ ảnh xem trước
let currentImageURL = null;

// Hàm xử lý ảnh
function handleImage(file) {

    if (!file) return;

    
    // Chỉ chấp nhận JPG, JPEG và PNG
const allowedTypes = [
    "image/jpeg",
    "image/png"
];

if (!allowedTypes.includes(file.type)) {
    uploadStatus.textContent =
        "Vui lòng chọn ảnh JPG, JPEG hoặc PNG!";
    return;
}

    // Kiểm tra dung lượng
    if (file.size > MAX_FILE_SIZE) {
        uploadStatus.textContent = "Ảnh không được vượt quá 5MB!";
        return;
    }

    // Xóa ảnh xem trước cũ
    if (currentImageURL) {
        URL.revokeObjectURL(currentImageURL);
    }

    // Tạo ảnh xem trước mới
    currentImageURL = URL.createObjectURL(file);

    imagePreview.src = currentImageURL;
    imagePreview.style.display = "block";

    uploadStatus.textContent =
        "Đã chọn ảnh thành công: " + file.name;
}

// Chọn ảnh từ máy tính
imageInput.addEventListener("change", function () {
    handleImage(imageInput.files[0]);
});

// Khi kéo ảnh vào khung
dropArea.addEventListener("dragover", function (event) {
    event.preventDefault();
    dropArea.style.backgroundColor = "#eaf4ff";
});

// Khi kéo ảnh ra khỏi khung
dropArea.addEventListener("dragleave", function () {
    dropArea.style.backgroundColor = "";
});

// Khi thả ảnh vào khung
dropArea.addEventListener("drop", function (event) {
    event.preventDefault();
    dropArea.style.backgroundColor = "";

    const file = event.dataTransfer.files[0];
    handleImage(file);
});

// Xóa ảnh
clearButton.addEventListener("click", function () {

    imagePreview.src = "";
    imagePreview.style.display = "none";

    imageInput.value = "";

    if (currentImageURL) {
        URL.revokeObjectURL(currentImageURL);
        currentImageURL = null;
    }

    uploadStatus.textContent =
        "Đã xóa ảnh. Bạn có thể chọn ảnh mới.";
});
