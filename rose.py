import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageTk
import math
import random

class BezierPetal:
    
    @staticmethod
    def compute_cubic_point(p0, p1, p2, p3, t):
        x = (1-t)**3 * p0[0] + 3*(1-t)**2 * t * p1[0] + 3*(1-t) * t**2 * p2[0] + t**3 * p3[0]
        y = (1-t)**3 * p0[1] + 3*(1-t)**2 * t * p1[1] + 3*(1-t) * t**2 * p2[1] + t**3 * p3[1]
        return (x, y)

    @classmethod
    def generate_petal_shape(cls, center, scale, rotation, deformation=0):
        cx, cy = center
        rad = math.radians(rotation)
        
        p0 = (0, 0)
        p1 = (-40 - deformation, -60 * scale)
        p2 = (40 + deformation, -60 * scale)
        p3 = (0, -100 * scale)
        
        raw_points = []
        for i in range(21):
            t = i / 20.0
            raw_points.append(cls.compute_cubic_point(p0, p1, p3, p3, t))
        for i in range(21):
            t = i / 20.0
            raw_points.append(cls.compute_cubic_point(p3, p2, p0, p0, t))

        transformed_points = []
        for x, y in raw_points:
            rx = x * math.cos(rad) - y * math.sin(rad) + cx
            ry = x * math.sin(rad) + y * math.cos(rad) + cy
            transformed_points.append((rx, ry))
            
        return transformed_points

class GradientRenderer:
    
    @staticmethod
    def interpolate_color(color1, color2, factor):
        """Hex အရောင်နှစ်ခုကို ရောစပ်ပေးခြင်း"""
        c1 = [int(color1[i:i+2], 16) for i in (1, 3, 5)]
        c2 = [int(color2[i:i+2], 16) for i in (1, 3, 5)]
        r = int(c1[0] + (c2[0] - c1[0]) * factor)
        g = int(c1[1] + (c2[1] - c1[1]) * factor)
        b = int(c1[2] + (c2[2] - c1[2]) * factor)
        return f"#{r:02x}{g:02x}{b:02x}"

    @classmethod
    def render_petal_gradient(cls, draw, points, base_color, tip_color, layers=15):
        if len(points) < 3:
            return
            
        cx = sum(p[0] for p in points) / len(points)
        cy = sum(p[1] for p in points) / len(points)
        
        for i in range(layers):
            factor = i / float(layers)
            current_color = cls.interpolate_color(base_color, tip_color, factor)
            
            scaled_points = []
            for p in points:
                sx = cx + (p[0] - cx) * (1.0 - factor * 0.4)
                sy = cy + (p[1] - cy) * (1.0 - factor * 0.4)
                scaled_points.append((sx, sy))
                
            draw.polygon(scaled_points, fill=current_color)

class ShadowRenderer:
    
    @staticmethod
    def render_polygon_shadow(image, points, offset=(3, 5), blur_iterations=2):
        shadow_mask = Image.new("RGBA", image.size, (0, 0, 0, 0))
        mask_draw = ImageDraw.Draw(shadow_mask)
        
        # ရွှေ့ထားသော အရိပ်အမှတ်များ
        shadow_points = [(p[0] + offset[0], p[1] + offset[1]) for p in points]
        mask_draw.polygon(shadow_points, fill=(10, 2, 2, 80))
        
        image.alpha_composite(shadow_mask)

class SpiralBloom:
    
    def __init__(self, center, config):
        self.center = center
        self.config = config # config dictionary ပါဝင်သည်

    def generate_all_petals(self):
        petals_data = []
        num_petals = self.config.get("num_petals", 65)
        golden_angle = 137.5
        
        for i in range(1, num_petals + 1):
            # Fermat's Spiral Formula: r = c * sqrt(n)
            theta = i * math.radians(golden_angle)
            r = self.config.get("spiral_density", 12.0) * math.sqrt(i)
            
            # အလယ်ဗဟိုမှ တည်နေရာ
            x = self.center[0] + r * math.cos(theta)
            y = self.center[1] + r * math.sin(theta)
            
            scale = 0.3 + (math.sqrt(i) / math.sqrt(num_petals)) * self.config.get("max_scale", 1.8)
            rotation = math.degrees(theta) + 90
            
            deformation = random.uniform(-5, 5) * (i / num_petals)
            
            petals_data.append({
                "center": (x, y),
                "scale": scale,
                "rotation": rotation,
                "deformation": deformation,
                "index": i
            })
            
        return petals_data

class SepalGenerator:
    
    @staticmethod
    def generate_sepals(center, base_radius, count=5):
        sepal_list = []
        cx, cy = center
        for i in range(count):
            angle = math.radians(i * (360 / count) + 18)
            p0 = (cx + (base_radius - 10) * math.cos(angle - 0.3), cy + (base_radius - 10) * math.sin(angle - 0.3))
            p1 = (cx + (base_radius + 40) * math.cos(angle), cy + (base_radius + 40) * math.sin(angle))
            p2 = (cx + (base_radius - 10) * math.cos(angle + 0.3), cy + (base_radius - 10) * math.sin(angle + 0.3))
            sepal_list.append([p0, p1, p2])
        return sepal_list

class StemGenerator:
    
    @staticmethod
    def generate_stem_path(start_pos, length, sway=30):
        points = []
        cx, cy = start_pos
        segments = 30
        for i in range(segments + 1):
            t = i / float(segments)
            curr_y = cy + t * length
            curr_x = cx + math.sin(t * math.pi) * sway
            points.append((curr_x, curr_y))
        return points

class LeafGenerator:
    
    @staticmethod
    def generate_leaf_pair(stem_points, index=15):
        if index >= len(stem_points):
            index = len(stem_points) // 2
            
        attach_point = stem_points[index]
        ax, ay = attach_point
        
        right_leaf = [
            attach_point,
            (ax + 40, ay - 10),
            (ax + 90, ay + 10), # ရွက်ထိပ်
            (ax + 50, ay + 40),
            attach_point
        ]
        
        left_leaf = [
            attach_point,
            (ax - 40, ay - 5),
            (ax - 85, ay + 20),
            (ax - 45, ay + 45),
            attach_point
        ]
        
        return left_leaf, right_leaf

class LightingEngine:
    
    def __init__(self, light_source=(200, 100, 300)):
        self.light_source = light_source # X, Y, Z coordinates

    def apply_lighting(self, color_hex, normal_vector):
        # Hex to RGB
        r = int(color_hex[1:3], 16) / 255.0
        g = int(color_hex[3:5], 16) / 255.0
        b = int(color_hex[5:7], 16) / 255.0
        
        lx, ly, lz = self.light_source
        mag = math.sqrt(lx**2 + ly**2 + lz**2)
        lx, ly, lz = lx/mag, ly/mag, lz/mag
        
        nx, ny, nz = normal_vector
        
        ambient = 0.35
        
        dot_product = nx*lx + ny*ly + nz*lz
        diffuse = max(0.0, dot_product) * 0.65
        
        # Total Intensity
        intensity = ambient + diffuse
        intensity = min(1.0, intensity)
        
        final_r = int(r * intensity * 255)
        final_g = int(g * intensity * 255)
        final_b = int(b * intensity * 255)
        
        return f"#{final_r:02x}{final_g:02x}{final_b:02x}"

class RoseEngine:
    
    def __init__(self, width=800, height=800):
        self.width = width
        self.height = height
        self.image = Image.new("RGBA", (width, height), (255, 255, 255, 255))
        self.draw = ImageDraw.Draw(self.image)
        self.lighting = LightingEngine()

    def clear_canvas(self):
        self.image = Image.new("RGBA", (self.width, self.height), (255, 255, 255, 255))
        self.draw = ImageDraw.Draw(self.image)

    def render_rose(self, config, progress_callback=None):
        self.clear_canvas()
        center = (self.width // 2, self.height // 2 - 50)
        
        stem_path = StemGenerator.generate_stem_path(center, 320, config.get("stem_sway", 25))
        for i in range(len(stem_path) - 1):
            self.draw.line([stem_path[i], stem_path[i+1]], fill="#1b4332", width=config.get("stem_width", 7))
            
        left_leaf, right_leaf = LeafGenerator.generate_leaf_pair(stem_path, index=14)
        GradientRenderer.render_petal_gradient(self.draw, left_leaf, "#2d6a4f", "#74c69d", layers=8)
        GradientRenderer.render_petal_gradient(self.draw, right_leaf, "#1b4332", "#52b788", layers=8)

        sepals = SepalGenerator.generate_sepals(center, base_radius=20, count=5)
        for sepal_points in sepals:
            GradientRenderer.render_petal_gradient(self.draw, sepal_points, "#40916c", "#1b4332", layers=6)

        bloom_system = SpiralBloom(center, config)
        all_petals = bloom_system.generate_all_petals()
        
        base_color = config.get("base_color", "#7a0010")
        tip_color = config.get("tip_color", "#ff4d6d")
        
        total_petals = len(all_petals)
        for idx, p_data in enumerate(all_petals):
            points = BezierPetal.generate_petal_shape(
                p_data["center"], p_data["scale"], p_data["rotation"], p_data["deformation"]
            )
            
            rad = math.radians(p_data["rotation"])
            normal = (math.cos(rad), math.sin(rad), 0.5)
            lit_base = self.lighting.apply_lighting(base_color, normal)
            lit_tip = self.lighting.apply_lighting(tip_color, normal)
            
            ShadowRenderer.render_polygon_shadow(self.image, points)
            GradientRenderer.render_petal_gradient(self.draw, points, lit_base, lit_tip, layers=12)
            
            if progress_callback and idx % 3 == 0:
                progress_callback(int((idx / total_petals) * 100))
                
        if progress_callback:
            progress_callback(100)
            
        return self.image

class ExportPNG:
    
    @staticmethod
    def save(image):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Files", "*.png"), ("All Files", "*.*")]
        )
        if file_path:
            image.save(file_path, "PNG")
            messagebox.showinfo("Success", "နှင်းဆီရုပ်ပုံအား PNG ဖိုင်အဖြစ် အောင်မြင်စွာ သိမ်းဆည်းပြီးပါပြီ။")

class AnimationEngine:
    
    def __init__(self, canvas, engine, config_func):
        self.canvas = canvas
        self.engine = engine
        self.get_config = config_func
        self.is_animating = False

    def animate_bloom(self):
        if self.is_animating:
            return
        self.is_animating = True
        
        config = self.get_config()
        self.engine.clear_canvas()
        center = (self.engine.width // 2, self.engine.height // 2 - 50)
        
        stem_path = StemGenerator.generate_stem_path(center, 320, config.get("stem_sway", 25))
        for i in range(len(stem_path) - 1):
            self.engine.draw.line([stem_path[i], stem_path[i+1]], fill="#1b4332", width=config.get("stem_width", 7))
        left_leaf, right_leaf = LeafGenerator.generate_leaf_pair(stem_path, index=14)
        GradientRenderer.render_petal_gradient(self.engine.draw, left_leaf, "#2d6a4f", "#74c69d", layers=8)
        GradientRenderer.render_petal_gradient(self.engine.draw, right_leaf, "#1b4332", "#52b788", layers=8)
        
        bloom_system = SpiralBloom(center, config)
        all_petals = bloom_system.generate_all_petals()
        
        def render_step(step=0):
            if not self.is_animating or step >= len(all_petals):
                self.is_animating = False
                return
                
            p_data = all_petals[step]
            points = BezierPetal.generate_petal_shape(
                p_data["center"], p_data["scale"], p_data["rotation"], p_data["deformation"]
            )
            
            rad = math.radians(p_data["rotation"])
            normal = (math.cos(rad), math.sin(rad), 0.5)
            lit_base = self.engine.lighting.apply_lighting(config["base_color"], normal)
            lit_tip = self.lighting_adjusted_color(config["tip_color"], normal)
            
            ShadowRenderer.render_polygon_shadow(self.engine.image, points)
            GradientRenderer.render_petal_gradient(self.engine.draw, points, lit_base, lit_tip, layers=10)
            
            self.tk_image = ImageTk.PhotoImage(self.engine.image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
            
            self.canvas.after(15, lambda: render_step(step + 1))

        render_step(0)

    def lighting_adjusted_color(self, color, normal):
        return self.engine.lighting.apply_lighting(color, normal)

class RoseGeneratorApp:
    
    def __init__(self, root):
        self.root = root
        self.root.title("HBD-81")
        self.root.geometry("845x663")
        self.root.configure(bg="#f4f4f6")
        
        self.engine = RoseEngine(400, 500)
        self.current_img = None
        
        self.setup_ui_layout()
        self.animation_engine = AnimationEngine(self.canvas, self.engine, self.get_current_config)
        self.generate_rose_image()

    def setup_ui_layout(self):
        # ဘယ်ဘက် Control Panel Framework
        control_panel = tk.Frame(self.root, bg="#ffffff", width=360, bd=1, relief=tk.SOLID)
        control_panel.pack(side=tk.LEFT, fill=tk.Y, padx=15, pady=15)
        control_panel.pack_propagate(False)
        
        title = tk.Label(control_panel, text="Settings", font=("Helvetica", 14, "bold"), bg="#ffffff", fg="#2b2d42")
        title.pack(pady=5)
        
        # Sliders Configuration Dictionary
        self.sliders = {}
        configs = [
            ("Petal Count (ပွင့်ဖတ်အရေအတွက်)", "num_petals", 30, 120, 45),
            ("Max Petal Scale (ပွင့်ဖတ်အရွယ်အစား)", "max_scale", 1.0, 3.0, 1.1),
            ("Spiral Density (ပွင့်ဖတ်သိပ်သည်းဆ)", "spiral_density", 5.0, 20.0, 5.5),
            ("Stem Width (ရိုးတံအကျယ်)", "stem_width", 3, 15, 10),
            ("Stem Curve/Sway (ရိုးတံကွေးညွတ်မှု)", "stem_sway", 0, 60, 40)
        ]
        
        for label_text, key, min_v, max_v, default_v in configs:
            frame = tk.Frame(control_panel, bg="#ffffff")
            frame.pack(fill=tk.X, padx=15, pady=8)
            lbl = tk.Label(frame, text=label_text, font=("Helvetica", 9), bg="#ffffff", fg="#555555")
            lbl.pack(anchor=tk.W)
            
            scl = tk.Scale(frame, from_=min_v, to=max_v, resolution=0.1 if isinstance(max_v, float) else 1,
                           orient=tk.HORIZONTAL, bg="#ffffff", bd=0, highlightthickness=0)
            scl.set(default_v)
            scl.pack(fill=tk.X)
            self.sliders[key] = scl

        # Colors Palette Selection
        color_frame = tk.Frame(control_panel, bg="#ffffff")
        color_frame.pack(fill=tk.X, padx=15, pady=10)
        # tk.Label(color_frame, text="Rose Color Preset", font=("Helvetica", 10, "bold"), bg="#ffffff").pack(anchor=tk.W)
        
        self.color_var = tk.StringVar(value="Classic Red")
        presets = ["Classic Red", "Deep Crimson", "Sunset Orange", "Soft Pink", "Mystic Purple"]
        self.color_menu = tk.OptionMenu(color_frame, self.color_var, *presets, command=lambda _: self.generate_rose_image())
        self.color_menu.pack(fill=tk.X, pady=5)

        # Progress Bar Area
        self.progress_lbl = tk.Label(control_panel, text="Status: Ready", font=("Helvetica", 10), bg="#ffffff", fg="#06d6a0")
        # self.progress_lbl.pack(pady=10)

        # Control Buttons
        btn_generate = tk.Button(control_panel, text="Render Instant Rose", command=self.generate_rose_image,
                                 bg="#4cc9f0", fg="white", font=("Helvetica", 11, "bold"), bd=0, pady=8)
        btn_generate.pack(fill=tk.X, padx=15, pady=5)
        
        btn_animate = tk.Button(control_panel, text="Animate Growing Process", command=self.trigger_animation,
                                bg="#7209b7", fg="white", font=("Helvetica", 11, "bold"), bd=0, pady=8)
        btn_animate.pack(fill=tk.X, padx=15, pady=5)
        
        btn_save = tk.Button(control_panel, text="Export HQ Image (PNG)", command=self.export_image,
                             bg="#4f5d75", fg="white", font=("Helvetica", 11, "bold"), bd=0, pady=8)
        btn_save.pack(fill=tk.X, padx=15, pady=5)

        self.canvas_frame = tk.Frame(self.root, bg="#ffffff", bd=1, relief=tk.SOLID)
        self.canvas_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=15, pady=15)
        
        self.canvas = tk.Canvas(self.canvas_frame, width=750, height=750, bg="#ffffff", highlightthickness=0)
        self.canvas.pack(expand=True, fill=tk.BOTH)

    def get_current_config(self):
        config = {k: v.get() for k, v in self.sliders.items()}
        
        # Color Map Presets
        color_maps = {
            "Classic Red": ("#A10A0A", "#ff3355"),
            "Deep Crimson": ("#4a0005", "#a4161a"),
            "Sunset Orange": ("#d03b0d", "#ffb703"),
            "Soft Pink": ("#ff8fa3", "#fff0f3"),
            "Mystic Purple": ("#3c096c", "#c77dff")
        }
        base, tip = color_maps.get(self.color_var.get(), ("#800000", "#ff3355"))
        config["base_color"] = base
        config["tip_color"] = tip
        
        return config

    def update_progress(self, percent):
        self.progress_lbl.config(text=f"Rendering Matrix: {percent}%", fg="#f77f00")
        self.root.update_idletasks()
        if percent == 100:
            self.progress_lbl.config(text="Status: Core Render Completed", fg="#06d6a0")

    def generate_rose_image(self):
        if hasattr(self, 'animation_engine'):
            self.animation_engine.is_animating = False
            
        config = self.get_current_config()
        self.current_img = self.engine.render_rose(config, progress_callback=self.update_progress)
        
        self.tk_img = ImageTk.PhotoImage(self.current_img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_img)

    def trigger_animation(self):
        self.generate_rose_image() # Reset Engine
        self.progress_lbl.config(text="Status: Simulating Growth Matrix...", fg="#7209b7")
        self.animation_engine.animate_bloom()

    def export_image(self):
        if self.current_img:
            ExportPNG.save(self.current_img)

if __name__ == "__main__":
    root = tk.Tk()
    
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    WINDOW_WIDTH = 845
    WINDOW_HEIGHT = 750
    
    pos_x = (screen_width - WINDOW_WIDTH) // 2
    pos_y = (screen_height - WINDOW_HEIGHT) // 2
    
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{pos_x}+{pos_y}")
    root.minsize(800, 580)
    
    # run app
    app = RoseGeneratorApp(root)
    root.mainloop()