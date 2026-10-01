// Standoff hanger for the flip-counter board.
// Two brackets (left + right) screw to the wall and hold the board
// 6" out from it by pins through the board's two existing corner holes.
// All dimensions in mm.

/* [Board] */
board_w       = 288.9;   // 11 3/8"
board_h       = 168.3;   // 6 5/8"
hole_spacing  = 264.7;   // ~10 7/16" center-to-center
hole_d        = 6.35;    // 1/4"
board_t       = 4.76;    // 3/16"

/* [Bracket] */
standoff      = 152.4;   // wall to back face of board (6")
arm_w         = 16;      // bracket width (print height)
arm_top       = 6;       // arm top, relative to hole center
arm_bot       = -14;     // arm bottom, relative to hole center
plate_t       = 5;       // wall plate thickness
plate_top     = 22;
plate_bot     = -92;
gusset_reach  = 100;     // where the brace meets the arm
gusset_bot    = -76;
web           = 6;       // truss member thickness
screw_d       = 4.5;     // #8 screw clearance
screw_head_d  = 9;
screw_z       = [14, -84];

/* [Pin] */
pin_d         = hole_d - 1.6;                 // loose fit in the hole
pin_flat      = pin_d * 0.8;                  // flats so it prints without support
pin_len       = board_t + 1.0;                // shoulder to retaining nub
nub_rise      = hole_d - 0.4 - pin_d;         // lift the board this much to remove
nub_len       = 3;

$fn = 48;

module profile_2d() {
    // arm
    translate([0, arm_bot]) square([standoff, arm_top - arm_bot]);
    // wall plate
    translate([0, plate_bot]) square([plate_t, plate_top - plate_bot]);
    // open triangular brace under the arm
    difference() {
        polygon([[0, gusset_bot], [plate_t, gusset_bot],
                 [gusset_reach, arm_bot], [0, arm_bot]]);
        offset(delta = -web)
            polygon([[0, gusset_bot], [plate_t, gusset_bot],
                     [gusset_reach, arm_bot], [0, arm_bot]]);
    }
}

module pin() {
    // D-flat pin, flush with the y=0 face so it sits on the print bed
    intersection() {
        // starts 1 mm inside the arm so it fuses into one solid
        translate([standoff - 1, pin_flat/2, 0]) rotate([0, 90, 0])
            cylinder(d = pin_d, h = pin_len + nub_len + 1);
        translate([standoff - 1, 0, -pin_d]) cube([pin_len + nub_len + 1, pin_flat, 2*pin_d]);
    }
    // retaining nub: board drops behind it under its own weight
    translate([standoff + pin_len, 0, 0])
        cube([nub_len, pin_flat, pin_d/2 + nub_rise]);
}

module screw_holes() {
    for (z = screw_z) translate([-1, arm_w/2, z]) rotate([0, 90, 0]) {
        cylinder(d = screw_d, h = plate_t + 2);
        // countersink on the front face
        translate([0, 0, plate_t + 1 - (screw_head_d - screw_d)/2])
            cylinder(d1 = screw_d, d2 = screw_head_d, h = (screw_head_d - screw_d)/2 + 0.01);
    }
}

// Model coords: x = out from wall, y = across, z = up; pin on the y=0 face.
module bracket() {
    difference() {
        rotate([90, 0, 0]) translate([0, 0, -arm_w]) linear_extrude(arm_w) profile_2d();
        screw_holes();
    }
    pin();
}

// Pin sits on the inner side so the arm stays outside the flipped cards.
module bracket_left()  { mirror([0, 1, 0]) bracket(); }
module bracket_right() { bracket(); }


part = "both"; // [left, right, both, assembly]

// Print poses: laid on the side with the pin face down, so no supports.
if (part == "left")  rotate([-90, 0, 0]) bracket_left();
if (part == "right") rotate([90, 0, 0]) bracket_right();
if (part == "both") {
    rotate([-90, 0, 0]) bracket_left();
    translate([0, 130, 0]) rotate([90, 0, 0]) bracket_right();
}
if (part == "assembly") {
    // wall at x=0, holes at y = +/- hole_spacing/2
    color("tan") translate([standoff, -board_w/2, -(board_h - 11)])
        difference() {
            cube([board_t, board_w, board_h]);
            for (s = [-1, 1]) translate([-1, board_w/2 + s*hole_spacing/2, board_h - 11])
                rotate([0, 90, 0]) cylinder(d = hole_d, h = board_t + 2);
        }
    color("steelblue") {
        // viewed from the front, +y is the right-hand side
        translate([0,  hole_spacing/2 - pin_flat/2, 0]) bracket_right();
        translate([0, -hole_spacing/2 + pin_flat/2, 0]) bracket_left();
    }
    color("#ddd", 0.4) translate([-2, -200, -150]) cube([2, 400, 220]);
}
