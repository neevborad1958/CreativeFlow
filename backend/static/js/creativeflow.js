// CreativeFlow — Vanilla JavaScript Client Engine (ES6+)

document.addEventListener('DOMContentLoaded', () => {
  initSlicedHeroParallax();
  initCanvasStudioArtifact();
  initKanbanDragAndDrop();
  initTabSwitchers();
  initModals();
});

/* 1. Sliced-Screen 3D Hero Dynamic Mouse Parallax */
function initSlicedHeroParallax() {
  const stage = document.querySelector('.hero-stage-3d');
  const container = document.querySelector('.slices-container');
  if (!stage || !container) return;

  stage.addEventListener('mousemove', (e) => {
    const rect = stage.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width - 0.5;
    const y = (e.clientY - rect.top) / rect.height - 0.5;

    const rotY = x * 14;
    const rotX = -y * 12;

    container.style.transform = `rotateY(${rotY}deg) rotateX(${rotX}deg)`;
  });

  stage.addEventListener('mouseleave', () => {
    container.style.transform = 'rotateY(0deg) rotateX(0deg)';
  });
}

/* 2. Canvas 3D Floating Studio Scene (Vanilla Canvas 2D/3D Projection) */
function initCanvasStudioArtifact() {
  const canvas = document.getElementById('studioCanvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  let animationId;
  let angle = 0;

  function resize() {
    canvas.width = canvas.parentElement.clientWidth || 600;
    canvas.height = 360;
  }
  resize();
  window.addEventListener('resize', resize);

  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const cx = canvas.width / 2;
    const cy = canvas.height / 2;

    angle += 0.015;
    const floatY = Math.sin(angle) * 12;

    // Background glow
    const grad = ctx.createRadialGradient(cx, cy, 10, cx, cy, 200);
    grad.addColorStop(0, 'rgba(215, 247, 165, 0.25)');
    grad.addColorStop(1, 'rgba(248, 244, 236, 0)');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Bottom Base Card (Deep Forest Green)
    ctx.save();
    ctx.translate(cx - 20, cy + floatY + 15);
    ctx.rotate(-0.08 + Math.sin(angle * 0.7) * 0.03);
    ctx.fillStyle = '#52664D';
    ctx.shadowColor = 'rgba(32, 36, 30, 0.2)';
    ctx.shadowBlur = 24;
    ctx.shadowOffsetY = 14;
    roundRect(ctx, -140, -85, 280, 170, 20);
    ctx.fill();

    // Subtle inner text/specs
    ctx.fillStyle = 'rgba(215, 247, 165, 0.4)';
    ctx.font = '10px JetBrains Mono';
    ctx.fillText('DESIGN SYSTEM TOKENS v2.4', -115, -55);
    ctx.restore();

    // Middle Accent Layer (Lime Glow)
    ctx.save();
    ctx.translate(cx + 10, cy + floatY);
    ctx.rotate(0.06 + Math.cos(angle * 0.8) * 0.02);
    ctx.fillStyle = '#D7F7A5';
    ctx.shadowColor = 'rgba(32, 36, 30, 0.15)';
    ctx.shadowBlur = 18;
    ctx.shadowOffsetY = 8;
    roundRect(ctx, -130, -80, 260, 160, 18);
    ctx.fill();

    ctx.fillStyle = '#20241E';
    ctx.font = 'bold 12px Plus Jakarta Sans';
    ctx.fillText('Lumina Platform UI Component Library', -105, -45);
    ctx.fillStyle = 'rgba(32, 36, 30, 0.6)';
    ctx.font = '10px Plus Jakarta Sans';
    ctx.fillText('Figma Tokens • 48 Components Approved', -105, -25);
    ctx.restore();

    // Top Translucent Card (Pure Surface Glass)
    ctx.save();
    ctx.translate(cx, cy + floatY - 20);
    ctx.rotate(-0.03 + Math.sin(angle * 0.9) * 0.02);
    ctx.fillStyle = 'rgba(255, 253, 247, 0.95)';
    ctx.shadowColor = 'rgba(32, 36, 30, 0.12)';
    ctx.shadowBlur = 28;
    ctx.shadowOffsetY = 18;
    roundRect(ctx, -125, -75, 250, 150, 16);
    ctx.fill();

    // Glass stroke
    ctx.strokeStyle = 'rgba(82, 102, 77, 0.3)';
    ctx.lineWidth = 1.5;
    ctx.stroke();

    ctx.fillStyle = '#52664D';
    ctx.font = 'bold 14px Newsreader';
    ctx.fillText('Milestone 01 Sign-off', -100, -35);

    ctx.fillStyle = '#77776F';
    ctx.font = '10px JetBrains Mono';
    ctx.fillText('REVISION ALLOWANCE: 1/3 USED', -100, -12);

    ctx.fillStyle = '#D7F7A5';
    roundRect(ctx, -100, 8, 90, 22, 6);
    ctx.fill();
    ctx.fillStyle = '#20241E';
    ctx.font = 'bold 9px JetBrains Mono';
    ctx.fillText('STATUS: OK', -85, 23);

    ctx.restore();

    animationId = requestAnimationFrame(draw);
  }

  function roundRect(c, x, y, w, h, r) {
    c.beginPath();
    c.moveTo(x + r, y);
    c.arcTo(x + w, y, x + w, y + h, r);
    c.arcTo(x + w, y + h, x, y + h, r);
    c.arcTo(x, y + h, x, y, r);
    c.arcTo(x, y, x + w, y, r);
    c.closePath();
  }

  draw();
}

/* 3. Interactive Kanban Board Drag and Drop */
function initKanbanDragAndDrop() {
  const cards = document.querySelectorAll('.task-card');
  const cols = document.querySelectorAll('.kanban-col');

  cards.forEach(card => {
    card.addEventListener('dragstart', (e) => {
      e.dataTransfer.setData('text/plain', card.getAttribute('data-task-id'));
      card.style.opacity = '0.5';
    });

    card.addEventListener('dragend', () => {
      card.style.opacity = '1';
    });
  });

  cols.forEach(col => {
    col.addEventListener('dragover', (e) => {
      e.preventDefault();
      col.style.background = 'rgba(215, 247, 165, 0.2)';
    });

    col.addEventListener('dragleave', () => {
      col.style.background = '';
    });

    col.addEventListener('drop', async (e) => {
      e.preventDefault();
      col.style.background = '';
      const taskId = e.dataTransfer.getData('text/plain');
      const targetStatus = col.getAttribute('data-status');
      const card = document.querySelector(`.task-card[data-task-id="${taskId}"]`);

      if (card && targetStatus) {
        col.querySelector('.tasks-container').appendChild(card);

        // Submit to Python Django endpoint
        const formData = new FormData();
        formData.append('task_id', taskId);
        formData.append('status', targetStatus);

        const csrfToken = getCsrfToken();
        try {
          await fetch('/dashboard/tasks/update-status/', {
            method: 'POST',
            body: formData,
            headers: { 'X-CSRFToken': csrfToken }
          });
        } catch (err) {
          console.error('Failed to sync task status:', err);
        }
      }
    });
  });
}

/* 4. Tab Switchers in Project Detail */
function initTabSwitchers() {
  const tabButtons = document.querySelectorAll('.tab-btn');
  const tabPanels = document.querySelectorAll('.tab-panel');

  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const target = btn.getAttribute('data-target');

      tabButtons.forEach(b => {
        b.classList.remove('btn-primary');
        b.classList.add('btn-secondary');
      });
      btn.classList.remove('btn-secondary');
      btn.classList.add('btn-primary');

      tabPanels.forEach(p => {
        p.style.display = p.id === target ? 'block' : 'none';
      });
    });
  });
}

/* 5. Modals */
function initModals() {
  window.openModal = function(id) {
    const m = document.getElementById(id);
    if (m) m.style.display = 'flex';
  };

  window.closeModal = function(id) {
    const m = document.getElementById(id);
    if (m) m.style.display = 'none';
  };
}

function getCsrfToken() {
  const name = 'csrftoken';
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue || '';
}

