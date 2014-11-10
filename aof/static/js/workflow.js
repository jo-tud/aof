CanvasRenderingContext2D.prototype.roundRect = 
function(x, y, width, height, radius, status, dx, dy, content) { 
    if (typeof radius === "undefined") { 
    radius = 5; 
    }
    this.beginPath(); 
    this.moveTo(x + radius, y); 
    this.lineTo(x + width - radius, y); 
    this.quadraticCurveTo(x + width, y, x + width, y + radius); 
    this.lineTo(x + width, y + height - radius); 
    this.quadraticCurveTo(x + width, y + height, x + width - radius, y+ height); 
    this.lineTo(x + radius, y + height); 
    this.quadraticCurveTo(x, y + height, x, y + height - radius); 
    this.lineTo(x, y + radius); 
    this.quadraticCurveTo(x, y, x + radius, y); 
    this.closePath(); 
    if (status == 1) {
        this.fillStyle = "#AA0000";
        this.fill(); 
    }
    if (status == 2) {
        this.fillStyle = "#00AA00";
        this.fill(); 
    }
    this.font = "Bold 20px Arial";
    this.fillStyle = "#000000"; 
    this.textAlign = "left";
    this.fillText(content, x + dx, y + dy);
}; 

CanvasRenderingContext2D.prototype.arrow =
function(sx, sy, ex, ey, lx, ly, rx, ry) {
    this.strokeStyle='#000';
    this.lineWidth=1;
    this.lineCap='butt';
    this.beginPath();
    this.moveTo(sx, sy);
    this.lineTo(ex, ey);
    this.lineTo(lx, ly);
    this.moveTo(ex, ey);
    this.lineTo(rx, ry);
    this.stroke();
    this.closePath();
}
