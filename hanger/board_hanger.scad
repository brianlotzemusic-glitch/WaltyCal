// Standoff hanger for the flip-counter board.
// Two brackets (left + right) screw to the wall and hold the board
// 6" out from it by pins through the board's two existing corner holes.
// The long arms run just outside the board's side edges so cards
// flipping over the rings never touch them.
// All dimensions in mm.

/* [Board] */
board_w       = 288.9;   // 11 3/8"
board_h       = 168.3;   // 6 5/8"
hole_spacing  = 264.7;   // ~10 7/16" center-to-center
hole_d        = 6.35;    // 1/4"
board_t       = 4.76;    // 3/16"
hole_from_top = 11;      // only used for the assembly preview

/* [Bracket] */
standoff      = 152.4;   // wall to back face of board (6")
edge_gap      = 3;       // arm clearance outside the board edge
arm_w         = 14;      // arm width
arm_h         = 16;      // arm height
pad_t         = 6;       // pad behind the board that carries the pin
pad_h         = 12;
plate_t       = 6;       // wall plate thickness
plate_drop    = 100;     // plate length below the top face
tab_w         = 14;      // outer tab for the upper screw
tab_h         = 20;
gusset_reach  = 60;      // brace meets the arm here (keeps it >45 deg)
gusset_drop   = 80;
web           = 6;       // brace member thickness
screw_d       = 4.5;     // #8 screw clearance
screw_head_d  = 9;

/* [Pin] */
pin_d         = hole_d - 1.6;              // loose fit in the hole
pin_h         = 4.0;                       // flats top and bottom
pin_len       = board_t + 1.0;             // pad face to retaining nub
nub_rise      = hole_d - 0.6 - pin_h;      // lift the board this much to remove
nub_len       = 3;

$fn = 48;

// Model coords (right-hand bracket): x = out from wall, y = outward along
// the board, z = up. Hole/pin center at y = 0, z = 0.
edge   = (board_w - hole_spacing) / 2;     // hole center to board edge
ztop   = pin_h/2 + nub_rise;               // shared top face = print bed
arm_y0 = edge + edge_gap;
arm_y1 = arm_y0 + arm_w;

module brace_2d() {
    tri = [[0, -arm_h], [gusset_reach, -arm_h], [0, -gusset_drop]];
    difference() {
        polygon(tri);
        offset(delta = -web) polygon(tri);
    }
}

module screw_hole(y, z) {
    translate([-1, y, z]) rotate([0, 90, 0]) {
        cylinder(d = screw_d, h = plate_t + 2);
        // countersink on the front face
        translate([0, 0, plate_t + 1 - (screw_head_d - screw_d)/2])
            cylinder(d1 = screw_d, d2 = screw_head_d, h = (screw_head_d - screw_d)/2 + 0.01);
    }
}

module pin() {
    intersection() {
        // starts 1 mm inside the pad so it fuses into one solid
        translate([standoff - 1, 0, 0]) rotate([0, 90, 0])
            cylinder(d = pin_d, h = pin_len + nub_len + 1);
        translate([standoff - 1, -pin_d, -pin_h/2]) cube([pin_len + nub_len + 1, 2*pin_d, pin_h]);
    }
    // retaining nub: board drops behind it under its own weight
    translate([standoff + pin_len, -pin_d/2, -pin_h/2])
        cube([nub_len, pin_d, ztop + pin_h/2]);
}

module bracket() {
    difference() {
        union() {
            // arm, outside the board edge
            translate([0, arm_y0, ztop - arm_h]) cube([standoff, arm_w, arm_h]);
            // pad behind the board corner, from the pin out to the arm
            translate([standoff - pad_t, -pin_d/2, ztop - pad_h])
                cube([pad_t, arm_y1 + pin_d/2, pad_h]);
            // wall plate + outer tab
            translate([0, arm_y0, ztop - plate_drop]) cube([plate_t, arm_w, plate_drop]);
            translate([0, arm_y0, ztop - tab_h]) cube([plate_t, arm_w + tab_w, tab_h]);
            // open triangular brace under the arm
            translate([0, arm_y1, ztop]) rotate([90, 0, 0]) linear_extrude(arm_w) brace_2d();
        }
        screw_hole(arm_y1 + tab_w/2, ztop - tab_h/2);
        screw_hole((arm_y0 + arm_y1)/2, ztop - plate_drop + 8);
    }
    pin();
}

module bracket_right() { bracket(); }
module bracket_left()  { mirror([0, 1, 0]) bracket(); }

// Print pose: upside down, so the shared top face sits on the bed.
// No supports needed (the pin bridges ~6 mm from pad to nub).
module print_pose() { translate([0, 0, ztop]) rotate([180, 0, 0]) children(); }

part = "both"; // [left, right, both, assembly]

if (part == "left")  print_pose() bracket_left();
if (part == "right") print_pose() bracket_right();
if (part == "both") {
    print_pose() bracket_left();
    translate([0, 70, 0]) print_pose() bracket_right();
}
if (part == "assembly") {
    // wall at x=0, viewed from the front +y is the right-hand side
    color("tan") translate([standoff, -board_w/2, -(board_h - hole_from_top)])
        difference() {
            cube([board_t, board_w, board_h]);
            for (s = [-1, 1]) translate([-1, board_w/2 + s*hole_spacing/2, board_h - hole_from_top])
                rotate([0, 90, 0]) cylinder(d = hole_d, h = board_t + 2);
        }
    color("steelblue") {
        translate([0,  hole_spacing/2, 0]) bracket_right();
        translate([0, -hole_spacing/2, 0]) bracket_left();
    }
    color("#ddd", 0.4) translate([-2, -220, -150]) cube([2, 440, 220]);
}

echo(str("Upper screws apart: ", hole_spacing + 2*(arm_y1 + tab_w/2), " mm, ",
         ztop - tab_h/2, " mm from pin center"));
echo(str("Lower screws apart: ", hole_spacing + (arm_y0 + arm_y1), " mm, ",
         ztop - plate_drop + 8, " mm from pin center"));
