import math
import datetime as dt
from const import *
from util import *
from dataclasses import dataclass, field
from typing import Tuple

def derivatives(s: Tuple[float, ...],
                rudder: float,
                throttle: float,
                max_acc_kn_s: float,
                drag_coeff: float ) -> Tuple[float, ...]:
    """
    Return ds/dt for the submarine.
    s = (x, y, vx, vy, psi)
    rudder  : rad / s   (be careful, convert from your rad/min input)
    throttle: -100 .. +100 (percent)
    """
    x, y, vx, vy, psi = s

    # -- 1. turning --------------------
    dpsi = rudder                         # rad/s

    # -- 2. thrust ---------------------
    ax_thrust = vec_from_angle(psi, max_acc_kn_s * throttle / 100)

    # -- 3. drag -----------------------
    speed = math.hypot(vx, vy)
    if speed == 0.0:
        ax_drag, ay_drag = 0.0, 0.0
    else:
        drag = cfg.drag_coeff * speed * speed        # kn/s
        ax_drag = -drag * vx / speed
        ay_drag = -drag * vy / speed

    ax = ax_thrust[0] + ax_drag
    ay = ax_thrust[1] + ay_drag

    # -- assemble derivative -----------
    return (
        vx,             # dx/dt
        vy,             # dy/dt
        ax,             # dvx/dt
        ay,             # dvy/dt
        dpsi            # dpsi/dt
    )



@dataclass
class Submarine:
    # --- configuration constants ---
    max_turn_rate_deg_min: float = 120.0             # deg/min
    max_speed_kn:          float = 36.0              # knots
    max_acc_kn_s:          float = 2.0               # knots/second  (throttle 100 %)
    drag_coeff:            float = 1.0               # tuned to taste

    # --- inputs (controls) ---
    rudder_rad_sec:  float = 0.0                     # radians/second (+ = port / CCW)
    throttle_pct:    float = 0.0                     # −100 … +100 %

    # --- state (updated every tick) ---
    pos_nm:   Vector = (0.0, 0.0)                    # position in nautical miles
    vel_kn:   Vector = (0.0, 0.0)                    # velocity in knots
    heading:  float  = 0.0                           # ship's bow direction (rad)
    clock:    dt.datetime = field(default_factory=lambda: dt.datetime(2022, 1, 1))

    # --------------------------------------------------------------------- #
    # public API                                                             #
    # --------------------------------------------------------------------- #

    def step2(self, dt_seconds: float) -> None:
        # convert rudder from rad/min to rad/s expected by derivative()
        rudder_rate = self.rudder_rad_sec

        # build current state tuple
        state = (*self.pos_nm, *self.vel_kn, self.heading)

        # one RK4 advance
        state = rk4_step(state, dt_seconds, rudder_rate, self.throttle_pct, self)

        # unpack back into object fields
        (x, y, vx, vy, psi) = state
        self.pos_nm = (x, y)
        self.vel_kn = (vx, vy)
        self.heading = psi % math.tau
        self.clock += dt.timedelta(seconds=dt_seconds)

        
    def step(self, dt_seconds: float) -> None:
        """Advance simulation by dt_seconds."""
        if dt_seconds <= 0:
            return

        # ----------------- convert constants to per-second ----------------
        max_turn_rate = math.radians(self.max_turn_rate_deg_min) / 60.0  # rad/s
        max_speed     = self.max_speed_kn
        max_acc       = self.max_acc_kn_s

        # ----------------- 1. heading update (rudder) ---------------------
        target_yaw_rate = max_turn_rate * self.rudder_rad_sec 
        self.heading += target_yaw_rate * dt_seconds
        self.heading = (self.heading + math.tau) % math.tau  # wrap 0…2π

        # ----------------- 2. thrust from turbines ------------------------
        thrust = max_acc * (self.throttle_pct / 100.0)       # kn/s
        thrust_vec = vec_from_angle(self.heading, thrust)

        # ----------------- 3. hydrodynamic drag ---------------------------
        speed = norm(self.vel_kn)
        drag_mag = self.drag_coeff * speed * speed           # kn/s opposite to vel
        drag_vec = (0.0, 0.0) if speed == 0 else tuple(
            -drag_mag * c / speed for c in self.vel_kn
        )

        # ----------------- 4. integrate velocity --------------------------
        ax, ay = (thrust_vec[0] + drag_vec[0],
                  thrust_vec[1] + drag_vec[1])
        self.vel_kn = (self.vel_kn[0] + ax * dt_seconds,
                       self.vel_kn[1] + ay * dt_seconds)

        # clamp to physical max speed
        speed = norm(self.vel_kn)
        if speed > max_speed:
            scale = max_speed / speed
            self.vel_kn = (self.vel_kn[0] * scale, self.vel_kn[1] * scale)

        # ----------------- 5. integrate position --------------------------
        self.pos_nm = (self.pos_nm[0] + self.vel_kn[0] * dt_seconds / SECONDS_PER_HOUR,
                       self.pos_nm[1] + self.vel_kn[1] * dt_seconds / SECONDS_PER_HOUR)

        # ----------------- 6. update wall clock ---------------------------
        self.clock += dt.timedelta(seconds=dt_seconds)

    # helper for display / logging
    def pretty_state(self) -> str:
        north, east = self.pos_nm[1], self.pos_nm[0]
        speed = norm(self.vel_kn)
        return (f"t={self.clock.time()}  pos=({east:.3f} E, {north:.3f} N) nm  "
                f"spd={speed:.2f} kn  hdg={math.degrees(self.heading):.1f}°")
        