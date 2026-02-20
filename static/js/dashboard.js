// Dashboard JavaScript Functions

function printResult() {
    window.print();
}

function downloadResult() {
    const element = document.getElementById('printable-result');
    const studentName = element.getAttribute('data-student-name');
    const rollNumber = element.getAttribute('data-roll-number');
    
    const opt = {
        margin: 10,
        filename: `Result_${rollNumber}_${studentName.replace(/\s+/g, '_')}.pdf`,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };
    
    // Show loading message
    const downloadBtn = event.target.closest('button');
    const originalText = downloadBtn.innerHTML;
    downloadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
    downloadBtn.disabled = true;
    
    html2pdf().set(opt).from(element).save().then(() => {
        downloadBtn.innerHTML = originalText;
        downloadBtn.disabled = false;
    }).catch(err => {
        console.error('Error generating PDF:', err);
        alert('Error generating PDF. Please try again.');
        downloadBtn.innerHTML = originalText;
        downloadBtn.disabled = false;
    });
}
