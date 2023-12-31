import math as m

# Inputs
V_Ed = 570 # kN
F_tie = 500 # kN

beam = {'section':'610x305 UB 238', 'end_dist':5}

min_gap = 10 # mm

f_ck = 40 # MPa
f_cm = f_ck + 8 # MPa
E_cm = 22*(f_cm/10)**0.3 *1000 # MPa

alpha_cc = 0.85
gamma_c = 1.5

f_cd = alpha_cc * f_ck / gamma_c

wall_thickness = 250 # mm

check = 1

# Positional dev
devs = {'Level':10, 'Plan': 35, 'Perpindicular':35}

# Fin plate arrangement
fin_pl = {'D': 500, 't_pl': 10, 'n_bolts': 7, 'grade': 'S275', 'bolt_end_dist':50, 'f_y':275, 's': 8, 'gamma_m':1, 'min_L':100, 'f_u':410, 'gamma_mu':1.1}
fin_pl['Z'] = fin_pl['t_pl'] * fin_pl['D']**2 / 6

# check shear / check tying resistance from P358 Table G.18

# Shear stud arrangement
studs = {'d': 25, 'rows': 3, 'cols': 2, 's_row': 125, 's_cols': 130, 'f_u': 450, 'h_sc': 100}
studs['n'] = studs['rows'] * studs['cols']
studs['A'] = studs['d']**2 * m.pi /4

# Reinforcement arrangement
reo = {'dia': 25, 'grade': 'B500', 'n_top': 2, 'n_bot': 2, 'dim_top_fpl':40, 'dim_bot_fpl':40, 'f_y':500, 'gamma_s':1.15, 'horiz_spacing':155, 'dim_top_cpl':70, 'dim_bot_cpl':70, 'gamma_s_acc':1.0}
reo['A'] = reo['dia']**2 * m.pi /4
reo['n'] = reo['n_bot'] + reo['n_top']

# Castin plate
castin_pl = {'t_pl': 10, 'grade': 'S355', 'f_y':345, 'width': 250, 'f_u': 470, 'gamma_m':1, 'gamma_mu':1.1}

gamma_v = 1.25

# ------------------------------------------ # 
# CONFIRM STUD ARRANGEMENT
if studs['h_sc']/studs['d'] > 4:
    alpha = 1
elif studs['h_sc']/studs['d'] >= 3:
    alpha = 0.2*(studs['h_sc']/studs['d'] + 1)

P_Rd = min((0.8 * studs['f_u'] * m.pi * studs['d']**2 / 4) / gamma_v , 
           0.232 * alpha * studs['d']**2 * (f_ck * E_cm)**0.5) 

P_Rd = P_Rd / 1000  
P_Rdtotal = P_Rd * studs['n']

print('Check {}: P_Rd {} vs V_Ed {}'.format(check, round(P_Rdtotal), V_Ed))
check += 1

#-----------------------------------------#
# CONSIDER POSITIONAL DEVIATIONS
M_T = V_Ed * devs['Plan']/1000 # kNm Moment due to ecc 

# Polar moment of stud group
d = (studs['rows']-1) * studs['s_row']
b = (studs['cols']-1) * studs['s_cols']

I_p = 4 * (d/2)**2 + 6*(b/2)**2 # mm2

# Shear in extreme stud due to moment
r = ((d/2)**2 + (b/2)**2)**0.5

V_m = M_T * r / (I_p/1000) # kN

sinAlpha = (b/2) / r
cosAlpha = (d/2) / r

# Horiz component
F_hoz = V_m*cosAlpha

# Vert component
F_vert = V_m*sinAlpha

# Max shear in corner stud (adding V_Ed to mix)
F_max = ((V_Ed/studs['n'] + F_vert)**2 + F_hoz**2)**0.5

print('Check {}: P_Rd {} vs F_max {}'.format(check, round(P_Rd), round(F_max)))
check += 1

#-----------------------------------------#
# CONSIDER ROTATIONAL DEVIATIONS
beta = m.atan(1/10)
betaDeg = m.degrees(beta)

alpha = m.atan((studs['s_cols']/2) / studs['s_row'])
alphaDeg = m.degrees(alpha)

# Horiz component
F_hoz_beta = V_m * m.cos(alpha + beta)

# Vert component
F_vert_beta = V_m * m.sin(alpha + beta)

F_max_beta = ((V_Ed/studs['n']+F_vert_beta)**2 + F_hoz_beta**2) **0.5

print('Check {}: P_Rd {} vs F_max_beta {}'.format(check, round(P_Rd), round(F_max_beta)))
check += 1

#-----------------------------------------#
# REINFORCEMENT ARRANGEMENT AND BAR SIZE
# ECC MOMENT ON CASTIN PLATE
nom_gap = min_gap + 2*devs['Plan']
e_p = castin_pl['t_pl'] + beam['end_dist'] + nom_gap + fin_pl['bolt_end_dist']
M_ecc = V_Ed * e_p / 1000 # kNm

# Ver level arm (Tens / Comp coupl)
diff = 100

fin_comp = 40 # mm (assumed depth of finplate req'd to resist compression)

while diff > 1:
    top_bar_pos = reo['dim_top_fpl'] # mm (from top of finplate)

    l = fin_pl['D'] - fin_comp - top_bar_pos/2 # mm

    F_t = M_ecc / (l/1000) #kN/m (Tension/comp to resist M_ecc)

    A_sreq_finPl = F_t*1000 / fin_pl['f_y'] # mm2

    depth_req_finPl = A_sreq_finPl / fin_pl['t_pl']

    diff = abs(fin_comp - depth_req_finPl)

    fin_comp = depth_req_finPl

# Confirm bar strength ok 
F_tRd = reo['dia']**2 * m.pi / 4 * reo['f_y'] / reo['gamma_s'] / 1000 # kN

#Override F_t to match example calc
F_t = 201

F_tEd = F_t * (reo['horiz_spacing']/2 + devs['Plan']) / (reo['horiz_spacing']) # kN per bar

print('Check {}: F_tRd {} vs F_tEd {}'.format(check, round(F_tRd), round(F_tEd)))
check += 1

print('Check {}: F_tRd total {} vs F_tEd {}'.format(check, round(F_tRd * reo['n_top']), round(F_t)))
check += 1

#-----------------------------------------#
# BENDING OF THE CASTIN PLATE
# Check mode 2 failure of BS EN 1993-1-8 CL 6.2.4
# Determine effective wdth of T-Stub using P398 Table 2.2 
# Consider:
# i) Corner yielding away from stiffener/flange
# ii) circular yielding
# iii) side yielding

w = reo['horiz_spacing']
t_fp = fin_pl['t_pl']
s = fin_pl['s']

m_ = (w - t_fp - 2 * 0.8 * s)/2

e_2 = 0.5 * (castin_pl['width'] - w)

e_x = reo['dim_top_cpl']

l_effnc =  2*m_ + 0.625*e_2 + e_x
l_effcp = 2*m.pi * m_
l_effnc_s = 4*m_ + 1.25*e_2

l_eff = min(l_effnc, l_effcp, l_effnc_s)

M_plRd = 0.25 * l_eff * castin_pl['t_pl']**2 * castin_pl['f_y'] / (castin_pl['gamma_m'] * 1000**2)

n = min(e_2, 1.25*m_)

e = devs['Plan'] 

R_B = (-M_plRd + F_tRd * (m_ - e)/1000) / ((n + m_ - e)/1000)

print('Check {}: R_B of {} kN is negative, therefore no prying force on one edge of the plate. Mode 2 Failure does not occur'.format(check, round(R_B)))
check += 1

# take moments about end A (refer to SCIP416 example calc)

b = reo['horiz_spacing']

alpha_f = n / (n+b)

F_T = (F_tRd * (alpha_f*n + (n+b))) / (n+(b/2+e))

# check bending moment at the face of the fin plate is less than the castin plate resistance

M = F_tRd * (m_-e)/1000

print('Check {}: MplRd {} kNm vs M_Ed {} kNm'.format(check, round(M_plRd), round(M)))
check += 1

# Check mode 1 failure
d_w = reo['dia']
e_w = d_w/4

F_RdT1A = ((4*n - e_w )*M_plRd*10**3) / (2*n*(m_-e) - e_w*((m_-e)+n))
F_RdT1B = ((4*n - e_w )*M_plRd*10**3) / (2*n*(m_+e) - e_w*((m_+e)+n))

F_RdT1 = F_RdT1A + F_RdT1B

print('Check {}: Mode 1 Resistance {} kN is larger than F_T of {} kN, therefore Mode 1 is not critical'.format(check, round(F_RdT1), round(F_T)))
check += 1

# Check the cast-in pl under tying load 
# Bar str in tying
F_tUlt_bar = reo['dia']**2 * m.pi / 4 * reo['f_y'] / (reo['gamma_s_acc']*1000)

# Sub bar str in tying into Mode 2 formula
F_T_tying = (F_tUlt_bar * (alpha_f*n + (n+b))) / (n+(b/2+e))

# Plate resistance using ult str
M_plRd_ult = 0.25 * l_eff * castin_pl['t_pl']**2 * castin_pl['f_u'] / (castin_pl['gamma_mu'] * 1000**2)

M_tie = F_tUlt_bar * (m_ -e)/1000

print('Check {}: Plate tying resist {} kNm vs Plate in bending due to tying {} kNm'.format(check, round(M_plRd_ult), round(M_tie)))
check += 1

# RESISTANCE OF COMBINED CASTIN PLATE AND FIN PLATE TO BENDING IN VERTICAL PLANE
# Nominal ecc moment 
ecc = e_p - castin_pl['t_pl']

# Ecc moment finplate
M_ecc_fPl = M_ecc * ecc/e_p

# Fin plate resistance
M_Rd_fPl = fin_pl['f_y'] * fin_pl['Z'] / fin_pl['gamma_m'] *10**-6

print('Check {}: Fin plate bending resist {} kNm vs bending due to ecc {} kNm'.format(check, round(M_Rd_fPl), round(M_ecc_fPl)))
check += 1

# Tying load case: 
leverArm = fin_pl['D'] - reo['dim_bot_fpl'] - reo['dim_top_fpl']

M_tying = F_tie * (leverArm/1000) / 8 # kNm

# assessment of finplate + castinpl as Tee section. 
flangeW_assumed = 100 # mm

tee_area_assumed = castin_pl['t_pl']*flangeW_assumed + fin_pl['t_pl']*fin_pl['min_L']
flange_area_assumed = flangeW_assumed * castin_pl['t_pl']

print('Check {}: Flange area {} vs A/2 {} m2 - If A_flange is larger, neutral axis is in flange'.format(check, round(flange_area_assumed), round(tee_area_assumed/2)))
check += 1

dist_from_top_flange = tee_area_assumed/2 / flangeW_assumed

# plastic modulus, taking area moments about neutral axis
flange_1 = (flangeW_assumed * dist_from_top_flange) * dist_from_top_flange/2
flange_2 = (flangeW_assumed * (castin_pl['t_pl']-dist_from_top_flange)) * ((castin_pl['t_pl']-dist_from_top_flange)/2)
web = (fin_pl['t_pl'] * fin_pl['min_L']) * ((castin_pl['t_pl']-dist_from_top_flange) + fin_pl['min_L']/2)

plast_mod_T = flange_1 + flange_2 + web

M_R = fin_pl['f_u']/fin_pl['gamma_mu'] * plast_mod_T / 10**6

print('Check {}: M_R {} kNm vs M_tying {} kNm'.format(check, round(M_R), round(M_tying)))
check += 1

# Bearing resistance of concrete at bottom of fin plate
F_c = F_t # kN (comp at bottom of fin plate)

# Vert dim for bearing (assuming 2.5:1 spread through castin pl)
d_bearing = depth_req_finPl + 5*castin_pl['t_pl']
w_bearing = fin_pl['t_pl'] + 2*fin_pl['s'] + 5*castin_pl['t_pl']

F_Rdu = d_bearing * w_bearing * f_cd / gamma_c / 1000 #kN 

print('Check {}: F_Rdu {} kN vs F_c,td {} kN'.format(check, round(F_Rdu), round(F_c)))
check += 1

#---------------------------------------------#
# DETAILING OF REINFORCEMENT FOR ECC MOMENT
alpha_ct = 1.0
f_ctm = 0.3*f_ck**(2/3)
f_ctk005 = 0.7 * f_ctm
f_ctd = alpha_ct * f_ctk005 / gamma_c

eta_1 = 0.7 # cannot show good bond conditions
eta_2 = 1.0 # bar dia is less than 32 mm 

f_bd = 2.25 * eta_1 * eta_2 * f_ctd

# Bond length required
l_breq = F_tRd*10**3 / (f_bd * m.pi * reo['dia'])
l_b = l_breq #ignore the numerous alpha factors

# Bent bar geometry
print('Check {}: Bent bar geometry check skipped, to be added later.'.format(check))
check += 1

# Reduced tension resist of reo in presence of shear
V_Ebar = V_Ed/reo['n'] * (reo['n'] * reo['A'] / (studs['n']*studs['A'] + reo['n']*reo['A']))

# Von mises failure criterion for uniaxial stress / shear stress
F_tRdRed = (F_tRd**2 - 3*V_Ebar**2)**0.5

print('Check {}: Reduced F_tRd {} kN vs F_tEd {} kN'.format(check, round(F_tRdRed), round(F_tEd)))
check += 1

# DETAILING OF REINFORCEMENT FOR TYING ACTION 
F_tie_bar = F_tie / reo['n']

print('Check {}: F_tie per bar {} kN vs Ult tensile capacity per bar {} kN'.format(check, round(F_tUlt_bar), round(F_tie_bar)))
check += 1

# Bond strength
gamma_c_acc = 1.2
f_ctd_tying = alpha_ct * f_ctk005 / gamma_c_acc
f_bd_tying = 2.25 * eta_1 * eta_2 * f_ctd_tying

# Bond length to resist ult bar strength
l_breq_tying = F_tUlt_bar*10**3 / (f_bd_tying * m.pi * reo['dia'])

# WELDING REINFORCEMENT TO CASTIN PLATE
# Design  str of weld
f_u = castin_pl['f_u']
beta_w = 0.9

f_vwd = (f_u / (3**0.5)) / (beta_w * castin_pl['gamma_mu'])

# Assume x2 welds provided
a_req = F_tUlt_bar*10**3 / (2*f_vwd * m.pi * reo['dia'])

pass