(function () {
  class RamayanaVisualizer {
    constructor(canvas) {
      this.canvas = canvas;
      this.ctx = canvas.getContext("2d");
      this.mode = "golden_rays";
      this.particles = [];
      this.lightningAlpha = 0;
      this.pulsePhase = 0;
      this.running = false;
      this.isPlaying = false;
      this.rafId = null;
      this.w = 1280;
      this.h = 720;
      this.resize();
      window.addEventListener("resize", () => this.resize());
    }

    resize() {
      const parent = this.canvas.parentElement;
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const cw = parent ? parent.clientWidth : window.innerWidth;
      const ch = parent ? parent.clientHeight : window.innerHeight;
      this.w = Math.max(320, cw);
      this.h = Math.max(240, ch);
      this.canvas.width = Math.floor(this.w * dpr);
      this.canvas.height = Math.floor(this.h * dpr);
      this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }

    setMode(mode) {
      if (this.mode === mode && this.particles.length) return;
      this.mode = mode || "golden_rays";
      this.initParticles();
    }

    setPlaying(playing) {
      this.isPlaying = playing;
    }

    initParticles() {
      const countMap = {
        golden_rays: 55,
        sacred_fire: 75,
        blossom_petals: 45,
        celestial_arrows: 50,
        twilight_sorrow: 50,
        mist_waterfall: 60,
        emerald_fireflies: 55,
        storm_lightning: 80,
        serene_lotus: 45,
        ocean_moonlight: 60,
        lanka_inferno: 95,
        sanjeevani_glow: 70,
        brahmastra_clash: 85,
        royal_diyas: 65,
        sarayu_eternal: 70
      };
      const n = countMap[this.mode] || 55;
      this.particles = [];
      for (let i = 0; i < n; i++) {
        this.particles.push(this.spawnParticle(true));
      }
    }

    spawnParticle(randomY = false) {
      const w = this.w;
      const h = this.h;
      const m = this.mode;
      const y = randomY ? Math.random() * h : (m === "sacred_fire" || m === "lanka_inferno" || m === "sanjeevani_glow" || m === "royal_diyas" || m === "sarayu_eternal" ? h + 20 : -20);
      return {
        x: Math.random() * w,
        y,
        r: 1.5 + Math.random() * 3.8,
        vx: (Math.random() - 0.5) * 0.8,
        vy: 0.4 + Math.random() * 1.4,
        alpha: 0.25 + Math.random() * 0.65,
        phase: Math.random() * Math.PI * 2,
        rot: Math.random() * Math.PI * 2,
        vrot: (Math.random() - 0.5) * 0.04,
        hue: Math.random()
      };
    }

    start() {
      if (this.running) return;
      this.running = true;
      if (!this.particles.length) this.initParticles();
      const loop = () => {
        if (!this.running) return;
        this.draw();
        this.rafId = requestAnimationFrame(loop);
      };
      this.rafId = requestAnimationFrame(loop);
    }

    stop() {
      this.running = false;
      if (this.rafId) cancelAnimationFrame(this.rafId);
      this.rafId = null;
    }

    draw() {
      const ctx = this.ctx;
      const w = this.w;
      const h = this.h;
      const m = this.mode;
      ctx.clearRect(0, 0, w, h);

      this.pulsePhase += this.isPlaying ? 0.025 : 0.008;

      // 1. Subtle volumetric sunbeams / aura
      if (m === "golden_rays" || m === "royal_diyas" || m === "sarayu_eternal" || m === "serene_lotus") {
        const gx = w * 0.5 + Math.sin(this.pulsePhase * 0.4) * (w * 0.08);
        const gy = h * 0.24;
        const grad = ctx.createRadialGradient(gx, gy, 10, gx, gy, Math.max(w, h) * 0.62);
        grad.addColorStop(0, "rgba(255, 224, 130, 0.16)");
        grad.addColorStop(0.5, "rgba(244, 169, 51, 0.06)");
        grad.addColorStop(1, "rgba(0, 0, 0, 0)");
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, w, h);
      }

      if (m === "sanjeevani_glow") {
        const grad = ctx.createRadialGradient(w * 0.5, h * 0.35, 20, w * 0.5, h * 0.35, Math.max(w, h) * 0.55);
        grad.addColorStop(0, "rgba(125, 255, 185, 0.16)");
        grad.addColorStop(1, "rgba(0,0,0,0)");
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, w, h);
      }

      if (m === "brahmastra_clash" || m === "celestial_arrows") {
        const cx = w * 0.5;
        const cy = h * 0.45;
        const r = 90 + Math.sin(this.pulsePhase * 1.6) * 28;
        ctx.save();
        ctx.translate(cx, cy);
        ctx.rotate(this.pulsePhase * 0.35);
        ctx.strokeStyle = "rgba(255, 226, 122, 0.16)";
        ctx.lineWidth = 1.6;
        ctx.beginPath();
        ctx.arc(0, 0, r, 0, Math.PI * 2);
        ctx.stroke();
        ctx.beginPath();
        ctx.arc(0, 0, r * 1.35, 0, Math.PI * 2);
        ctx.stroke();
        ctx.restore();
      }

      // 2. Storm lightning flash
      if (m === "storm_lightning" || m === "brahmastra_clash") {
        if (this.isPlaying && Math.random() < 0.008) {
          this.lightningAlpha = 0.42;
        }
        if (this.lightningAlpha > 0.01) {
          ctx.fillStyle = `rgba(215, 232, 255, ${this.lightningAlpha})`;
          ctx.fillRect(0, 0, w, h);
          this.lightningAlpha *= 0.85;
        }
      }

      // 3. Fire bottom glow
      if (m === "sacred_fire" || m === "lanka_inferno") {
        const fg = ctx.createLinearGradient(0, h * 0.55, 0, h);
        fg.addColorStop(0, "rgba(255, 95, 20, 0)");
        fg.addColorStop(1, m === "lanka_inferno" ? "rgba(255, 90, 15, 0.25)" : "rgba(255, 150, 40, 0.16)");
        ctx.fillStyle = fg;
        ctx.fillRect(0, h * 0.55, w, h * 0.45);
      }

      // 4. Particles
      const speedMul = this.isPlaying ? 1.0 : 0.35;
      for (let i = 0; i < this.particles.length; i++) {
        const p = this.particles[i];
        p.phase += 0.03 * speedMul;
        p.rot += p.vrot * speedMul;

        if (m === "blossom_petals") {
          p.y += p.vy * 0.75 * speedMul;
          p.x += (Math.sin(p.phase) * 0.9 + 0.35) * speedMul;
          ctx.save();
          ctx.translate(p.x, p.y);
          ctx.rotate(p.rot);
          ctx.fillStyle = p.hue > 0.5
            ? `rgba(255, 178, 196, ${p.alpha * 0.85})`
            : `rgba(255, 212, 110, ${p.alpha * 0.85})`;
          ctx.beginPath();
          ctx.ellipse(0, 0, p.r * 1.9, p.r * 0.95, 0, 0, Math.PI * 2);
          ctx.fill();
          ctx.restore();
          if (p.y > h + 20) Object.assign(p, this.spawnParticle(false));
        } else if (m === "storm_lightning" || m === "twilight_sorrow") {
          const isRain = m === "storm_lightning";
          p.y += p.vy * (isRain ? 7.5 : 1.1) * speedMul;
          p.x += (isRain ? -1.4 : Math.sin(p.phase) * 0.35) * speedMul;
          ctx.strokeStyle = isRain
            ? `rgba(185, 215, 255, ${p.alpha * 0.35})`
            : `rgba(210, 195, 235, ${p.alpha * 0.32})`;
          if (isRain) {
            ctx.lineWidth = 1.1;
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(p.x - 4, p.y + 15);
            ctx.stroke();
          } else {
            ctx.fillStyle = `rgba(215, 200, 240, ${p.alpha * 0.45})`;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r * 0.7, 0, Math.PI * 2);
            ctx.fill();
          }
          if (p.y > h + 20 || p.x < -20) Object.assign(p, this.spawnParticle(false));
        } else if (m === "sacred_fire" || m === "lanka_inferno") {
          p.y -= p.vy * (m === "lanka_inferno" ? 2.1 : 1.4) * speedMul;
          p.x += Math.sin(p.phase * 1.5) * 0.85 * speedMul;
          const col = p.hue > 0.35
            ? `rgba(255, 198, 72, ${p.alpha})`
            : `rgba(255, 96, 28, ${p.alpha})`;
          ctx.fillStyle = col;
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.r * 0.9, 0, Math.PI * 2);
          ctx.fill();
          if (p.y < -20) Object.assign(p, this.spawnParticle(false));
        } else if (m === "celestial_arrows" || m === "brahmastra_clash") {
          p.x += (p.hue > 0.5 ? 4.2 : -4.2) * speedMul;
          p.y += (Math.random() - 0.5) * 1.2 * speedMul;
          ctx.strokeStyle = p.hue > 0.4
            ? `rgba(255, 224, 120, ${p.alpha})`
            : `rgba(255, 145, 65, ${p.alpha})`;
          ctx.lineWidth = 2;
          ctx.beginPath();
          ctx.moveTo(p.x, p.y);
          ctx.lineTo(p.x + (p.hue > 0.5 ? -22 : 22), p.y);
          ctx.stroke();
          if (p.x < -40 || p.x > w + 40) {
            p.x = p.hue > 0.5 ? -10 : w + 10;
            p.y = Math.random() * h * 0.85;
          }
        } else if (m === "emerald_fireflies" || m === "sanjeevani_glow") {
          p.y -= p.vy * 0.65 * speedMul;
          p.x += Math.cos(p.phase) * 0.7 * speedMul;
          const pulse = 0.4 + 0.6 * Math.abs(Math.sin(p.phase * 1.4));
          ctx.fillStyle = m === "sanjeevani_glow"
            ? `rgba(130, 255, 185, ${p.alpha * pulse})`
            : `rgba(218, 255, 130, ${p.alpha * pulse})`;
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.r * 1.15, 0, Math.PI * 2);
          ctx.fill();
          if (p.y < -20) Object.assign(p, this.spawnParticle(false));
        } else if (m === "ocean_moonlight" || m === "mist_waterfall") {
          p.x += Math.sin(p.phase * 0.6) * 0.6 * speedMul;
          p.y += (m === "mist_waterfall" ? 0.5 : -0.35) * speedMul;
          const tw = 0.35 + 0.65 * Math.abs(Math.sin(p.phase));
          ctx.fillStyle = m === "ocean_moonlight"
            ? `rgba(205, 232, 255, ${p.alpha * tw})`
            : `rgba(225, 245, 255, ${p.alpha * 0.45})`;
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.r * 0.9, 0, Math.PI * 2);
          ctx.fill();
          if (p.y < -20 || p.y > h + 20) Object.assign(p, this.spawnParticle(true));
        } else {
          // golden_rays, serene_lotus, royal_diyas, sarayu_eternal
          p.y -= p.vy * 0.55 * speedMul;
          p.x += Math.sin(p.phase) * 0.45 * speedMul;
          const glow = 0.45 + 0.55 * Math.abs(Math.sin(p.phase));
          ctx.fillStyle = `rgba(255, 224, 128, ${p.alpha * glow})`;
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
          ctx.fill();
          if (p.y < -20) Object.assign(p, this.spawnParticle(false));
        }
      }
    }
  }

  window.RamayanaVisualizer = RamayanaVisualizer;
})();
