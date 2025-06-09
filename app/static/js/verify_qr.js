// Sử dụng thư viện html5-qrcode để quét mã QR từ webcam
// https://github.com/mebjas/html5-qrcode

document.addEventListener('DOMContentLoaded', function() {
    const qrButton = document.getElementById('start-qr-btn');
    const qrResultInput = document.getElementById('qr_verification_code');
    const qrReaderDiv = document.getElementById('qr-reader');
    let qrScanner = null;

    if (qrButton && qrReaderDiv) {
        qrButton.addEventListener('click', function() {
            qrReaderDiv.style.display = 'block';
            if (!qrScanner) {
                qrScanner = new Html5Qrcode("qr-reader");
                qrScanner.start(
                    { facingMode: "environment" },
                    {
                        fps: 10,
                        qrbox: 250
                    },
                    (decodedText, decodedResult) => {
                        qrResultInput.value = decodedText;
                        qrScanner.stop();
                        qrReaderDiv.style.display = 'none';
                    },
                    (errorMessage) => {
                        // ignore scan errors
                    }
                ).catch(err => {
                    alert("Không thể truy cập camera hoặc lỗi khi khởi động quét QR: " + err);
                });
            }
        });
    }
});
