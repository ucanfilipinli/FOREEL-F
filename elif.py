import math
import time
import webbrowser
import numpy as np
import pygame

# --- AYARLAR ---
W, H = 900, 900
FPS = 60
SPOTIFY_URL = "https://open.spotify.com/track/06JvOZ39sK8D8SqiqfaxDU?si=QYjWJaWfRdqUrkDi2-_9xw&utm_source=copy-link"

FONT_MAP = {
    "L": [
        "###      ",
        "###      ",
        "###      ",
        "###      ",
        "###      ",
        "###      ",
        "###      ",
        "#########",
        "#########",
    ],
    "I": [
        "#########",
        "#########",
        "   ###   ",
        "   ###   ",
        "   ###   ",
        "   ###   ",
        "   ###   ",
        "#########",
        "#########",
    ],
    "Y": [
        "###   ###",
        "###   ###",
        " ### ### ",
        "  #####  ",
        "   ###   ",
        "   ###   ",
        "   ###   ",
        "   ###   ",
        "   ###   ",
    ],
    "U": [
        "###   ###",
        "###   ###",
        "###   ###",
        "###   ###",
        "###   ###",
        "###   ###",
        "###   ###",
        "#########",
        " ####### ",
    ],
    "M": [
        "###   ###",
        "#### ####",
        "#########",
        "### # ###",
        "###   ###",
        "###   ###",
        "###   ###",
        "###   ###",
        "###   ###",
    ],
}


def smooth(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def lerp(a, b, t):
    return a + (b - a) * t


def midrib(t, e0, curl, c0, vs=370.0, k=40):
    """Taç yaprağın 3B uzaydaki merkez omurga eğrisini hesaplar."""
    us = np.linspace(0.0, 1.0, k + 1)
    a = e0 + curl * (us ** 1.65) - c0 * (us ** 2.4)
    ds = (t / k) * vs
    r = np.concatenate([[0.0], np.cumsum(np.sin(a[1:]) * ds)])
    h = np.concatenate([[0.0], np.cumsum(np.cos(a[1:]) * ds)])
    return us, r, h


def build_ascii_glyphs():
    pygame.font.init()
    font = pygame.font.SysFont("consolas", 13, bold=True)
    chars = ["@", "#", "*", "+", ":", "."]
    glyphs = {}
    for ch in chars:
        surf = font.render(ch, True, (255, 255, 255))
        arr = pygame.surfarray.array3d(surf).astype(np.float32) / 255.0
        glyphs[ch] = arr
    return glyphs


def create_text_particles(word="LILYUM"):
    glyphs = build_ascii_glyphs()
    char_list = ["@", "#", "*", "+", ":", "."]
    particles = []

    cell_w, cell_h = 11, 13
    letter_spacing = 18
    sample_w = len(FONT_MAP["L"][0]) * cell_w
    total_w = len(word) * sample_w + (len(word) - 1) * letter_spacing
    start_x = (W - total_w) // 2
    start_y = H // 2 - (9 * cell_h) // 2

    rng = np.random.default_rng(42)

    for idx, letter in enumerate(word):
        grid = FONT_MAP[letter]
        ox = start_x + idx * (sample_w + letter_spacing)
        for r_i, row in enumerate(grid):
            for c_i, val in enumerate(row):
                if val == "#":
                    
                    is_edge = (
                        r_i == 0
                        or r_i == len(grid) - 1
                        or c_i == 0
                        or c_i == len(row) - 1
                        or grid[r_i - 1][c_i] == " "
                        or grid[r_i + 1][c_i] == " "
                    )
                    ch = rng.choice(["+", ":", "."]) if is_edge else rng.choice(["@", "#", "*"])
                    px = ox + c_i * cell_w
                    py = start_y + r_i * cell_h

                
                    angle = rng.uniform(0, 2 * math.pi)
                    speed = rng.uniform(40, 220)
                    particles.append(
                        {
                            "x": float(px),
                            "y": float(py),
                            "glyph": glyphs[ch],
                            "vx": math.cos(angle) * speed,
                            "vy": math.sin(angle) * speed - rng.uniform(60, 180),
                            "phase": rng.uniform(0, 2 * math.pi),
                        }
                    )

   
    sparks = []
    for _ in range(180):
        sparks.append(
            {
                "dy": rng.uniform(-160, 160),
                "dx": rng.uniform(-55, 25),
                "size": rng.uniform(1.0, 2.5),
                "speed": rng.uniform(0.6, 1.5),
                "phase": rng.uniform(0, 6.28),
            }
        )
    return particles, sparks, start_x, start_x + total_w



def create_lily_data():
    rng = np.random.default_rng(108)

    
    n_stars = 260
    stars_x = rng.integers(0, W, size=n_stars)
    stars_y = rng.integers(0, int(H * 0.85), size=n_stars)
    stars_b = rng.uniform(0.25, 1.0, size=n_stars)
    stars_p = rng.uniform(0, 2 * np.pi, size=n_stars)

    
    n_soil = 3800
    so_x = rng.normal(0.0, 210.0, size=n_soil)
    so_z = rng.normal(0.0, 90.0, size=n_soil)
    so_y = (so_x ** 2) / 1450.0 + rng.normal(0.0, 3.5, size=n_soil) + so_z * 0.12
    so_col = np.stack(
        [
            rng.uniform(45, 95, n_soil),
            rng.uniform(55, 105, n_soil),
            rng.uniform(80, 130, n_soil),
        ],
        axis=1,
    )

    
    ns = 3200
    st_t = rng.random(ns)
    st_ang = rng.uniform(0, 2 * np.pi, ns)
    st_rad = rng.uniform(0.0, 4.2, ns) * (1.0 - 0.35 * st_t)
    st_col = np.stack(
        [
            lerp(35, 115, st_t) + rng.uniform(-10, 10, ns),
            lerp(165, 235, st_t) + rng.uniform(-12, 12, ns),
            lerp(75, 125, st_t) + rng.uniform(-10, 10, ns),
        ],
        axis=1,
    )

   
    leaf_specs = [
        (0.24, 135.0, 1.0, 0.55),
        (0.32, 155.0, -1.0, 0.62),
        (0.46, 140.0, 1.0, 0.50),
        (0.55, 120.0, -1.0, 0.48),
    ]
    leaves = []
    nl = 1100
    for h_frac, length, side, droop in leaf_specs:
        u = rng.random(nl) ** 0.85
        v = rng.uniform(-1.0, 1.0, nl)
        # Yaprak damarına yakın yoğunlaşma
        v = np.sign(v) * (np.abs(v) ** 0.75)
        width_profile = np.sin(np.pi * (u ** 0.7)) * 24.0
        z_off = rng.uniform(-4.0, 4.0, nl)

        
        vein = np.exp(-((v * 3.2) ** 2))
        col = np.stack(
            [
                lerp(40, 135, u) + vein * 45,
                lerp(175, 240, u) + vein * 20,
                lerp(75, 125, u) + vein * 30,
            ],
            axis=1,
        )
        leaves.append(
            {
                "h_frac": h_frac,
                "length": length,
                "side": side,
                "droop": droop,
                "u": u,
                "v": v,
                "w_prof": width_profile,
                "z_off": z_off,
                "col": col,
            }
        )

    
    np_petal = 2300
    petals = []
    for k in range(6):
        u = rng.random(np_petal) ** 0.82
        v = rng.uniform(-1.0, 1.0, np_petal)
        # Kenar ve orta damar vurgusu
        edge_bias = np.abs(v) ** 0.85
        v = np.sign(v) * edge_bias

       
        w_prof = np.sin(np.pi * (u ** 0.74)) * (1.0 - 0.18 * u) * 54.0

        
        throat = np.exp(-((u / 0.26) ** 2))
        midrib_line = np.exp(-((v * 5.0) ** 2)) * (1.0 - u * 0.6)

        r_c = lerp(235, 255, u) * (1.0 - 0.12 * midrib_line) + throat * 25
        g_c = lerp(65, 145, u ** 1.3) + throat * 155 + midrib_line * 35
        b_c = lerp(165, 215, u) - throat * 75 + midrib_line * 25

        
        spots = (u > 0.15) & (u < 0.58) & (np.abs(v) < 0.55) & (rng.random(np_petal) < 0.065)
        r_c[spots] *= 0.42
        g_c[spots] *= 0.25
        b_c[spots] *= 0.45

        col = np.clip(np.stack([r_c, g_c, b_c], axis=1), 0, 255)
        
        layer = k % 2
        azim = k * (2.0 * np.pi / 6.0)

        petals.append(
            {
                "u": u,
                "v": v,
                "w_prof": w_prof,
                "col": col,
                "azim": azim,
                "layer": layer,
            }
        )


    stamens = []
    for k in range(6):
        azim = k * (2.0 * np.pi / 6.0) + 0.25
        su = np.linspace(0.0, 1.0, 90)
        stamens.append({"azim": azim, "u": su})

    return {
        "stars": (stars_x, stars_y, stars_b, stars_p),
        "soil": (so_x, so_y, so_z, so_col),
        "stem": (st_t, st_ang, st_rad, st_col),
        "leaves": leaves,
        "petals": petals,
        "stamens": stamens,
    }



def accumulate_points(buf, xs, ys, cols):
    valid = (xs >= 1) & (xs < W - 1) & (ys >= 1) & (ys < H - 1)
    vx = xs[valid]
    vy = ys[valid]
    vc = cols[valid]
    np.add.at(buf, (vx, vy), vc)


def apply_bloom_and_blit(screen, buf, overlay_fn=None):
    
    small = buf[::4, ::4].copy()
    blur = (
        small
        + np.roll(small, 1, axis=0)
        + np.roll(small, -1, axis=0)
        + np.roll(small, 1, axis=1)
        + np.roll(small, -1, axis=1)
    ) / 5.0
    blur = (
        blur
        + np.roll(blur, 1, axis=0)
        + np.roll(blur, -1, axis=0)
        + np.roll(blur, 1, axis=1)
        + np.roll(blur, -1, axis=1)
    ) / 5.0

    bloom_up = np.repeat(np.repeat(blur, 4, axis=0), 4, axis=1)
    final_buf = np.clip(buf + bloom_up * 0.85, 0, 255).astype(np.uint8)
    pygame.surfarray.blit_array(screen, final_buf)

    if overlay_fn is not None:
        overlay_fn(screen)



def main():
    
    try:
        webbrowser.open(SPOTIFY_URL)
        time.sleep(1.8)  
    except Exception:
        pass

    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Lilyum")
    clock = pygame.time.Clock()

    text_particles, sparks, txt_x0, txt_x1 = create_text_particles("LILYUM")
    lily = create_lily_data()

    start_time = time.time()
    running = True

    T_TEXT_END = 6.2      
    T_TRANS_END = 8.4     

    while running:
        dt = clock.tick(FPS) / 1000.0
        t = time.time() - start_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    
                    start_time = time.time()
                    t = 0.0

        
        buf = np.zeros((W, H, 3), dtype=np.float32)
        buf[:, :, 0] = 5.0
        buf[:, :, 1] = 6.0
        buf[:, :, 2] = 14.0

        
        star_alpha = float(np.clip((t - 5.5) / 2.5, 0.15, 1.0))
        sx, sy, sb, sp = lily["stars"]
        twinkle = (0.65 + 0.35 * np.sin(t * 2.2 + sp)) * sb * star_alpha * 220.0
        star_cols = np.stack([twinkle * 0.85, twinkle * 0.9, twinkle * 1.1], axis=1)
        accumulate_points(buf, sx, sy, star_cols)

     
        if t < T_TRANS_END:
            
            sweep_prog = float(np.clip((t - 0.3) / 3.8, 0.0, 1.15))
            wave_x = lerp(txt_x0 - 40, txt_x1 + 60, sweep_prog)

            
            trans_p = float(np.clip((t - T_TEXT_END) / (T_TRANS_END - T_TEXT_END), 0.0, 1.0))
            ease_trans = trans_p * trans_p * (3.0 - 2.0 * trans_p)

            for p in text_particles:
                dist_wave = wave_x - p["x"]
                if dist_wave < -25:
                    continue

                
                reveal = float(np.clip((dist_wave + 25) / 45.0, 0.0, 1.0))
                flash = math.exp(-((dist_wave / 28.0) ** 2)) * (1.0 - ease_trans)

                
                px = p["x"] + p["vx"] * (ease_trans ** 1.3) * 1.6
                py = p["y"] + p["vy"] * (ease_trans ** 1.3) * 1.6

                
                r_col = lerp(245.0, 255.0, ease_trans) + flash * 80.0
                g_col = lerp(52.0, 115.0, ease_trans) + flash * 130.0
                b_col = lerp(38.0, 210.0, ease_trans) + flash * 90.0

                alpha = reveal * (1.0 - ease_trans * 0.95)
                if alpha <= 0.02:
                    continue

                ix, iy = int(px), int(py)
                glyph = p["glyph"]
                gw, gh = glyph.shape[0], glyph.shape[1]
                if 0 <= ix < W - gw and 0 <= iy < H - gh:
                    color_vec = np.array([r_col, g_col, b_col], dtype=np.float32) * alpha
                    buf[ix : ix + gw, iy : iy + gh] += glyph * color_vec

            
            if sweep_prog < 1.08 and trans_p == 0.0:
                sp_xs, sp_ys, sp_cols = [], [], []
                for sp_item in sparks:
                    ang = t * 3.0 * sp_item["speed"] + sp_item["phase"]
                    sx_p = int(wave_x + sp_item["dx"] + math.cos(ang) * 18.0)
                    sy_p = int(H // 2 + sp_item["dy"] + math.sin(ang) * 14.0)
                    sp_xs.append(sx_p)
                    sp_ys.append(sy_p)
                    sp_cols.append([255.0, 110.0, 60.0])
                accumulate_points(
                    buf,
                    np.array(sp_xs, dtype=np.int32),
                    np.array(sp_ys, dtype=np.int32),
                    np.array(sp_cols, dtype=np.float32),
                )

        
        flower_t = t - (T_TEXT_END + 0.6)
        if flower_t > 0.0:
            gx, gy = W / 2.0, H * 0.83
           
            cam_rot = 0.24 * math.sin(flower_t * 0.45)
            sway_x = 7.0 * math.cos(flower_t * 0.7)
            sway_y = 4.0 * math.sin(flower_t * 0.55)
            cos_r, sin_r = math.cos(cam_rot), math.sin(cam_rot)

            def project_3d(x3, y3, z3):
               
                rx = x3 * cos_r - z3 * sin_r
                rz = x3 * sin_r + z3 * cos_r
                persp = 1.0 + rz / 1400.0
                sx_p = (gx + sway_x + rx * persp).astype(np.int32)
                sy_p = (gy + sway_y - y3 * persp + rz * 0.22).astype(np.int32)
                return sx_p, sy_p

            
            soil_g = float(smooth(flower_t / 1.4))
            so_x, so_y, so_z, so_col = lily["soil"]
            sx_s, sy_s = project_3d(so_x, -so_y, so_z)
            accumulate_points(buf, sx_s, sy_s, so_col * soil_g * 0.85)

            
            stem_g = float(smooth((flower_t - 0.4) / 2.6))
            st_t, st_ang, st_rad, st_col = lily["stem"]
            mask_st = st_t <= stem_g
            if np.any(mask_st):
                t_sub = st_t[mask_st]
                stem_h = t_sub * 355.0
                stem_curve_x = np.sin(t_sub * 2.2) * 12.0
                x3 = stem_curve_x + np.cos(st_ang[mask_st]) * st_rad[mask_st]
                z3 = np.sin(st_ang[mask_st]) * st_rad[mask_st]
                sx_st, sy_st = project_3d(x3, stem_h, z3)
                accumulate_points(buf, sx_st, sy_st, st_col[mask_st])

           
            for idx, lf in enumerate(lily["leaves"]):
                lf_start = 1.2 + idx * 0.35
                lg = float(smooth((flower_t - lf_start) / 1.8))
                if lg <= 0.01:
                    continue
                u = lf["u"] * lg
                v = lf["v"]
                base_y = lf["h_frac"] * 355.0 * min(1.0, stem_g / lf["h_frac"] if lf["h_frac"] > 0 else 1.0)
                base_x = math.sin(lf["h_frac"] * 2.2) * 12.0

                reach = u * lf["length"] * lf["side"]
                arch_y = base_y + np.sin(u * np.pi * 0.72) * 48.0 - (u ** 2) * 28.0 * lf["droop"]
                z3 = v * lf["w_prof"] * lg + lf["z_off"]
                x3 = base_x + reach
                y3 = arch_y - np.abs(v) * 4.5

                sx_l, sy_l = project_3d(x3, y3, z3)
                accumulate_points(buf, sx_l, sy_l, lf["col"] * (0.4 + 0.6 * lg))

            
            bud_grow = float(smooth((flower_t - 2.4) / 2.2))
            bloom_open = float(smooth((flower_t - 3.6) / 3.8))

            if bud_grow > 0.01:
                top_y = 352.0 * stem_g
                top_x = math.sin(2.2) * 12.0 * stem_g

                for pt in lily["petals"]:
                    
                    base_tilt = 0.14 + (0.06 if pt["layer"] == 1 else 0.0)
                    open_tilt = 0.88 + (0.14 if pt["layer"] == 1 else 0.0)
                    e0 = lerp(base_tilt, open_tilt, bloom_open)
                    curl = lerp(0.12, 0.92, bloom_open)

                    us_grid, r_grid, h_grid = midrib(
                        t=bud_grow, e0=e0, curl=curl, c0=0.18, vs=185.0, k=50
                    )

                    u = pt["u"]
                    v = pt["v"]
                    r_p = np.interp(u, us_grid, r_grid)
                    h_p = np.interp(u, us_grid, h_grid)

                    
                    lat = v * pt["w_prof"] * bud_grow
                    cup = (1.0 - v * v) * 9.0 * bud_grow

                    
                    local_r = r_p + cup * 0.35
                    local_y = h_p + cup * 0.45
                    az = pt["azim"] + math.sin(flower_t * 0.5) * 0.04

                    x3 = top_x + local_r * math.cos(az) - lat * math.sin(az)
                    z3 = local_r * math.sin(az) + lat * math.cos(az)
                    y3 = top_y + local_y

                    sx_p, sy_p = project_3d(x3, y3, z3)
                    brightness = 0.55 + 0.45 * bud_grow
                    accumulate_points(buf, sx_p, sy_p, pt["col"] * brightness)

                
                if bloom_open > 0.15:
                    st_vis = float(smooth((bloom_open - 0.15) / 0.6))
                    for stm in lily["stamens"]:
                        su = stm["u"] * st_vis
                        sr = np.sin(su * 1.1) * 38.0 * bloom_open
                        sh = su * 105.0 * bud_grow
                        az = stm["azim"]
                        x3 = top_x + sr * math.cos(az)
                        z3 = sr * math.sin(az)
                        y3 = top_y + sh
                        sx_m, sy_m = project_3d(x3, y3, z3)
                        cols_m = np.tile(np.array([255.0, 215.0, 120.0]), (len(su), 1)) * st_vis
                        # Uç kısımdaki koyu turuncu polen başlığı
                        cols_m[-12:] = np.array([255.0, 110.0, 35.0]) * st_vis
                        accumulate_points(buf, sx_m, sy_m, cols_m)

            
            ring_alpha = int(np.clip((flower_t - 2.0) * 18.0, 0, 42))

            def draw_orbital_rings(surf):
                if ring_alpha <= 2:
                    return
                ring_surf = pygame.Surface((W, H), pygame.SRCALPHA)
                cx, cy = int(gx + sway_x), int(gy - 250 + sway_y)
                for r_idx, rad in enumerate([165, 245, 325]):
                    ox = int(cx + math.cos(flower_t * (0.35 + r_idx * 0.15) + r_idx) * 28)
                    oy = int(cy + math.sin(flower_t * (0.28 + r_idx * 0.12) + r_idx) * 22)
                    pygame.draw.circle(ring_surf, (165, 185, 235, ring_alpha), (ox, oy), rad, 1)
                surf.blit(ring_surf, (0, 0))

            apply_bloom_and_blit(screen, buf, draw_orbital_rings)
        else:
            apply_bloom_and_blit(screen, buf)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()