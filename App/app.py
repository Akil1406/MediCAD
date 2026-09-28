"""MediCAD: Parametric CAD Prototyping and Engineering Analysis Application.

Streamlit Web Studio & 3D Prototyping Workspace.
"""

import streamlit as st
import numpy as np
import pandas as pd
import json
import base64
import math
from pathlib import Path

from medcad.config import (
    APP_NAME, APP_VERSION, MEDICAL_DEVICE_DISCLAIMER, EXPORTS_DIR
)
from medcad.models.specs import (
    TubeSpec, CatheterSpec, TaperedTubeSpec,
    ConnectorSpec, InjectorSpec, PlungerSpec, AssemblySpec
)
from medcad.cad import (
    CAD_BUILDERS, build_tube, build_catheter, build_tapered_tube,
    build_connector, build_injector, build_plunger, build_syringe_assembly,
    export_step, export_stl, export_obj, export_design_package
)
from medcad.validation import run_full_validation
from medcad.materials import MaterialDatabase, evaluate_and_rank_materials
from medcad.models.materials import MaterialRequirements
from medcad.simulation import (
    BurstPressureSimulator, ColumnBucklingSimulator, SyringeFlowSimulator
)
from medcad.storage import DesignStorage, VersionComparator
from medcad.reports import generate_engineering_report
from medcad.agents import run_design_pipeline


# Page Configuration
st.set_page_config(
    page_title="MediCAD — Medical Tool CAD Builder",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for rich aesthetics and modern typography
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 50%, #4f46e5 100%);
        padding: 24px 28px;
        border-radius: 14px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.25);
    }
    
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    .disclaimer-banner {
        background-color: #fffbeb;
        border-left: 5px solid #f59e0b;
        padding: 12px 18px;
        border-radius: 8px;
        font-size: 0.88rem;
        color: #92400e;
        margin-bottom: 22px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.04);
    }
    
    .metric-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 14px 18px;
        text-align: center;
    }
    
    .status-pass {
        color: #15803d;
        font-weight: 600;
        background-color: #dcfce7;
        padding: 4px 10px;
        border-radius: 6px;
        display: inline-block;
    }
    
    .status-warn {
        color: #b45309;
        font-weight: 600;
        background-color: #fef3c7;
        padding: 4px 10px;
        border-radius: 6px;
        display: inline-block;
    }
    
    .status-fail {
        color: #b91c1c;
        font-weight: 600;
        background-color: #fee2e2;
        padding: 4px 10px;
        border-radius: 6px;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)


# Initialize Session State
if "db" not in st.session_state:
    st.session_state.db = MaterialDatabase()
if "storage" not in st.session_state:
    st.session_state.storage = DesignStorage()
if "current_design_id" not in st.session_state:
    st.session_state.current_design_id = "DES_CATH_001"
if "current_version" not in st.session_state:
    st.session_state.current_version = 1
if "latest_pipeline_state" not in st.session_state:
    st.session_state.latest_pipeline_state = None


# Header
st.markdown(f"""
<div class="main-header">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
            <h1>🩺 {APP_NAME} <span style="font-size:1rem; background:rgba(255,255,255,0.25); padding:3px 10px; border-radius:20px;">v{APP_VERSION}</span></h1>
            <p style="margin:6px 0 0 0; opacity:0.92; font-size:1.02rem;">Parametric CAD Prototyping & Engineering Analysis Assistant for Medical Tool Concepts</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Safety Notice
st.markdown(f"""
<div class="disclaimer-banner">
    ⚠️ <strong>SAFETY & REGULATORY BOUNDARY:</strong> {MEDICAL_DEVICE_DISCLAIMER}
</div>
""", unsafe_allow_html=True)


# Three.js 3D Mesh Viewer Helper
def render_3d_stl_viewer(mesh_bytes: bytes, height: int = 440, color: str = "#2563eb", wireframe: bool = False):
    b64_stl = base64.b64encode(mesh_bytes).decode("utf-8")
    wireframe_js = "true" if wireframe else "false"
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ margin: 0; padding: 0; overflow: hidden; background: #0f172a; border-radius: 12px; }}
            #canvas-container {{ width: 100%; height: {height}px; }}
            #info-overlay {{
                position: absolute;
                top: 12px;
                left: 14px;
                color: #94a3b8;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                font-size: 11px;
                pointer-events: none;
                background: rgba(15, 23, 42, 0.75);
                padding: 6px 10px;
                border-radius: 6px;
                backdrop-filter: blur(4px);
            }}
        </style>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/STLLoader.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    </head>
    <body>
        <div id="info-overlay">🖱️ Left Drag: Rotate | Right Drag: Pan | Scroll: Zoom</div>
        <div id="canvas-container"></div>
        <script>
            const container = document.getElementById('canvas-container');
            const scene = new THREE.Scene();
            scene.background = new THREE.Color(0x0f172a);

            const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 2000);
            const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
            renderer.setSize(container.clientWidth, container.clientHeight);
            renderer.setPixelRatio(window.devicePixelRatio);
            renderer.shadowMap.enabled = true;
            container.appendChild(renderer.domElement);

            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;

            // Studio Lighting
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
            scene.add(ambientLight);

            const dirLight1 = new THREE.DirectionalLight(0xffffff, 0.8);
            dirLight1.position.set(100, 200, 150);
            scene.add(dirLight1);

            const dirLight2 = new THREE.DirectionalLight(0x38bdf8, 0.5);
            dirLight2.position.set(-100, -100, -100);
            scene.add(dirLight2);

            // Grid
            const grid = new THREE.GridHelper(200, 20, 0x334155, 0x1e293b);
            grid.position.y = 0;
            scene.add(grid);

            // Load STL from base64
            const stlData = atob("{b64_stl}");
            const bytes = new Uint8Array(stlData.length);
            for (let i = 0; i < stlData.length; i++) {{
                bytes[i] = stlData.charCodeAt(i);
            }}

            const loader = new THREE.STLLoader();
            const geometry = loader.parse(bytes.buffer);
            geometry.center();

            const material = new THREE.MeshPhysicalMaterial({{
                color: "{color}",
                metalness: 0.15,
                roughness: 0.35,
                clearcoat: 0.3,
                clearcoatRoughness: 0.1,
                wireframe: {wireframe_js},
                side: THREE.DoubleSide
            }});

            const mesh = new THREE.Mesh(geometry, material);
            scene.add(mesh);

            // Position camera
            geometry.computeBoundingSphere();
            const radius = geometry.boundingSphere.radius;
            camera.position.set(radius * 1.8, radius * 1.5, radius * 2.2);
            camera.lookAt(0, 0, 0);
            controls.target.set(0, 0, 0);

            function animate() {{
                requestAnimationFrame(animate);
                controls.update();
                renderer.render(scene, camera);
            }}
            animate();

            window.addEventListener('resize', () => {{
                camera.aspect = container.clientWidth / container.clientHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(container.clientWidth, container.clientHeight);
            }});
        </script>
    </body>
    </html>
    """
    st.components.v1.html(html_code, height=height + 15)


# Sidebar - Navigation & Global Controls
st.sidebar.title("🩺 MediCAD Studio")
app_mode = st.sidebar.radio(
    "Active Workspace",
    [
        "🎯 AI Concept Studio",
        "🛠️ Parametric Workbench",
        "🌐 3D CAD Viewport",
        "🛡️ Validation & Rules",
        "🧪 Materials Engine",
        "⚡ Engineering Simulation",
        "📜 Design History & Diffs",
        "📦 Controlled Export Center"
    ]
)

st.sidebar.divider()
st.sidebar.markdown("### Active Device Profile")
selected_device_type = st.sidebar.selectbox(
    "Device Template",
    ["Catheter", "Straight Tube", "Tapered Shaft", "Luer Connector", "Syringe Barrel", "Plunger Rod", "Mated Syringe Assembly"],
    index=0
)

type_map = {
    "Catheter": "catheter",
    "Straight Tube": "tube",
    "Tapered Shaft": "tapered_tube",
    "Luer Connector": "connector",
    "Syringe Barrel": "injector",
    "Plunger Rod": "plunger",
    "Mated Syringe Assembly": "assembly"
}
active_dtype = type_map[selected_device_type]


# -------------------------------------------------------------
# TAB 1: AI CONCEPT STUDIO
# -------------------------------------------------------------
if app_mode == "🎯 AI Concept Studio":
    st.header("🎯 Natural Language AI Design Studio")
    st.markdown("Describe your medical device requirement, catheter shaft, or connector in plain language. The LangGraph agent will parse requirements, validate geometry, select registered templates, and build the CAD model.")

    col1, col2 = st.columns([3, 2])
    with col1:
        default_prompt = "Create a high-torque vascular catheter with length 150 mm, outer diameter 2.0 mm, inner lumen 1.2 mm, atraumatic tip length 5 mm with 15 deg bevel, and standard proximal luer hub."
        user_prompt = st.text_area("Design Intent Prompt", value=default_prompt, height=130)

        example_prompts = [
            "Straight medical extrusion tube 120 mm long, 3.0 mm OD, 2.0 mm ID.",
            "Tapered introducer dilator 100 mm long, 4.0 mm proximal OD, 1.8 mm distal tip OD, 1.0 mm inner lumen.",
            "Standard ISO male luer lock connector 22 mm long with 2 hose barbs.",
            "10 mL syringe barrel 85 mm long, 16 mm outer diameter, 14 mm bore, with standard luer tip."
        ]
        selected_ex = st.selectbox("Or load blueprint example:", ["(Choose example)"] + example_prompts)
        if selected_ex != "(Choose example)":
            user_prompt = selected_ex

        if st.button("🚀 Run Agentic Design Workflow", type="primary", use_container_width=True):
            with st.spinner("Executing LangGraph orchestrator workflow..."):
                pipeline_state = run_design_pipeline(user_prompt)
                st.session_state.latest_pipeline_state = pipeline_state
                st.success(f"✓ Successfully generated design for: {pipeline_state.get('target_device_type', 'device').upper()}")

    with col2:
        st.markdown("### Workflow Graph Progress")
        st.markdown("""
        ```text
        Intake Request
             ↓
        Extract Specifications
             ↓
        Validate Pydantic Schema
             ↓
        Deterministic CAD Engine
             ↓
        Level 1/2 Geometry Checks
             ↓
        Evaluate Medical Materials
             ↓
        Generate Prototyping Report
        ```
        """)

    if st.session_state.latest_pipeline_state:
        state = st.session_state.latest_pipeline_state
        st.divider()
        st.subheader("Agent Outcome & Extracted Specification")

        c1, c2, c3 = st.columns(3)
        c1.metric("Device Type", state.get("target_device_type", "").title())
        cad_res = state.get("cad_result", {})
        c2.metric("Solid Volume", f"{cad_res.get('volume_mm3', 0.0):.2f} mm³")
        c3.metric("Watertight Mesh", "✓ Watertight" if cad_res.get("is_watertight") else "Non-manifold")

        st.json(state.get("specification", {}))

        with st.expander("📄 View Generated Engineering Report"):
            st.markdown(state.get("engineering_report", ""))


# -------------------------------------------------------------
# TAB 2: PARAMETRIC WORKBENCH & 3D VIEWPORT
# -------------------------------------------------------------
elif app_mode in ("🛠️ Parametric Workbench", "🌐 3D CAD Viewport"):
    st.header(f"🛠️ Parametric CAD Workbench — {selected_device_type}")
    
    col_params, col_preview = st.columns([1.2, 1.8])

    with col_params:
        st.subheader("Parametric Dimensions")

        if active_dtype == "tube":
            length = st.number_input("Length (mm)", value=100.0, min_value=5.0, max_value=2000.0, step=5.0)
            od = st.number_input("Outer Diameter (mm)", value=3.0, min_value=0.2, max_value=50.0, step=0.1)
            id_val = st.number_input("Inner Diameter (mm)", value=2.0, min_value=0.1, max_value=od - 0.05, step=0.1)
            spec = TubeSpec(length_mm=length, outer_diameter_mm=od, inner_diameter_mm=id_val)
            mesh, cad_res = build_tube(spec)

        elif active_dtype == "catheter":
            length = st.number_input("Total Length (mm)", value=150.0, min_value=10.0, max_value=2500.0, step=10.0)
            od = st.number_input("Shaft Outer Diameter (mm)", value=2.0, min_value=0.3, max_value=20.0, step=0.1)
            id_val = st.number_input("Inner Lumen Diameter (mm)", value=1.2, min_value=0.1, max_value=od - 0.05, step=0.1)
            tip_len = st.number_input("Tip Taper Length (mm)", value=5.0, min_value=1.0, max_value=length * 0.4, step=0.5)
            tip_angle = st.slider("Tip Angle / Bevel (deg)", min_value=0.0, max_value=60.0, value=0.0, step=5.0)
            has_hub = st.checkbox("Include Proximal Luer Hub", value=True)
            spec = CatheterSpec(
                length_mm=length,
                outer_diameter_mm=od,
                inner_diameter_mm=id_val,
                tip_length_mm=tip_len,
                tip_angle_deg=tip_angle,
                has_luer_hub=has_hub
            )
            mesh, cad_res = build_catheter(spec)

        elif active_dtype == "tapered_tube":
            length = st.number_input("Length (mm)", value=120.0, min_value=10.0, max_value=1000.0, step=10.0)
            prox_od = st.number_input("Proximal OD (mm)", value=4.0, min_value=0.5, max_value=30.0, step=0.2)
            dist_od = st.number_input("Distal OD (mm)", value=2.0, min_value=0.3, max_value=prox_od, step=0.2)
            id_val = st.number_input("Inner Lumen (mm)", value=1.2, min_value=0.1, max_value=dist_od - 0.05, step=0.1)
            spec = TaperedTubeSpec(
                length_mm=length,
                proximal_outer_diameter_mm=prox_od,
                distal_outer_diameter_mm=dist_od,
                inner_diameter_mm=id_val
            )
            mesh, cad_res = build_tapered_tube(spec)

        elif active_dtype == "connector":
            length = st.number_input("Length (mm)", value=22.0, min_value=10.0, max_value=80.0, step=1.0)
            od = st.number_input("Collar Outer Diameter (mm)", value=6.5, min_value=3.0, max_value=20.0, step=0.5)
            id_val = st.number_input("Fluid Bore (mm)", value=2.5, min_value=0.5, max_value=od - 0.5, step=0.1)
            barbs = st.slider("Barbs Count", min_value=0, max_value=5, value=2)
            spec = ConnectorSpec(
                length_mm=length,
                outer_diameter_mm=od,
                inner_diameter_mm=id_val,
                barb_count=barbs
            )
            mesh, cad_res = build_connector(spec)

        elif active_dtype == "injector":
            b_len = st.number_input("Barrel Length (mm)", value=80.0, min_value=20.0, max_value=300.0, step=5.0)
            b_od = st.number_input("Barrel OD (mm)", value=16.0, min_value=5.0, max_value=60.0, step=1.0)
            b_id = st.number_input("Barrel Bore ID (mm)", value=14.0, min_value=4.0, max_value=b_od - 0.5, step=1.0)
            flange = st.number_input("Finger Flange Width (mm)", value=24.0, min_value=b_od + 2.0, max_value=80.0, step=1.0)
            spec = InjectorSpec(
                body_length_mm=b_len,
                body_outer_diameter_mm=b_od,
                body_inner_diameter_mm=b_id,
                flange_width_mm=flange
            )
            mesh, cad_res = build_injector(spec)

        elif active_dtype == "plunger":
            p_len = st.number_input("Plunger Length (mm)", value=90.0, min_value=30.0, max_value=300.0, step=5.0)
            h_od = st.number_input("Head Sealing Diameter (mm)", value=13.9, min_value=3.0, max_value=60.0, step=0.1)
            r_od = st.number_input("Rod Core Diameter (mm)", value=6.0, min_value=1.5, max_value=h_od - 1.0, step=0.5)
            spec = PlungerSpec(
                plunger_length_mm=p_len,
                head_outer_diameter_mm=h_od,
                rod_diameter_mm=r_od
            )
            mesh, cad_res = build_plunger(spec)

        elif active_dtype == "assembly":
            st.markdown("**Syringe + Plunger Assembly Controls**")
            b_len = st.number_input("Barrel Length (mm)", value=80.0)
            b_od = st.number_input("Barrel OD (mm)", value=16.0)
            b_id = st.number_input("Barrel Bore (mm)", value=14.0)
            h_od = st.number_input("Plunger Head OD (mm)", value=13.9)
            
            inj_spec = InjectorSpec(body_length_mm=b_len, body_outer_diameter_mm=b_od, body_inner_diameter_mm=b_id, flange_width_mm=24.0)
            plu_spec = PlungerSpec(plunger_length_mm=b_len + 15.0, head_outer_diameter_mm=h_od, rod_diameter_mm=6.0)
            assy_spec = AssemblySpec(injector_spec=inj_spec, plunger_spec=plu_spec)
            mesh, cad_res, analysis = build_syringe_assembly(assy_spec)
            spec = assy_spec

        # Save to session state
        st.session_state.current_spec = spec
        st.session_state.current_mesh = mesh
        st.session_state.current_cad_res = cad_res

        # Save version button
        if st.button("💾 Save as Immutable Version", use_container_width=True):
            val_rep = run_full_validation(spec, cad_res)
            v_num = st.session_state.storage.save_design_version(
                design_id=st.session_state.current_design_id,
                title=f"{selected_device_type} Design",
                device_type=active_dtype,
                specification=spec.model_dump(),
                cad_properties=cad_res.model_dump(),
                validation_report=val_rep.model_dump(),
                user_prompt=f"Parametric update: {selected_device_type}"
            )
            st.session_state.current_version = v_num
            st.success(f"✓ Saved as Immutable Version v{v_num}")

    with col_preview:
        st.subheader("3D Interactive Viewport")
        
        view_col1, view_col2, view_col3 = st.columns([1, 1, 1])
        with view_col1:
            wireframe_mode = st.toggle("Wireframe Mode", value=False)
        with view_col2:
            model_color = st.color_picker("Render Color", value="#38bdf8")
        with view_col3:
            st.metric("Solid Volume", f"{cad_res.volume_mm3:.2f} mm³")

        render_3d_stl_viewer(mesh.to_stl_bytes(), height=420, color=model_color, wireframe=wireframe_mode)

        # Derived property tags
        st.markdown("### Derived CAD Quantities")
        prop_cols = st.columns(4)
        prop_keys = list(cad_res.derived_parameters.items())[:4]
        for i, (k, v) in enumerate(prop_keys):
            with prop_cols[i]:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size:0.75rem; color:#64748b; text-transform:uppercase;">{k.replace('_', ' ')}</div>
                    <div style="font-size:1.1rem; font-weight:600; color:#0f172a;">{f"{v:.3f}" if isinstance(v, float) else v}</div>
                </div>
                """, unsafe_allow_html=True)


# -------------------------------------------------------------
# TAB 3: VALIDATION & DESIGN RULES
# -------------------------------------------------------------
elif app_mode == "🛡️ Validation & Rules":
    st.header("🛡️ Engineering & Geometric Validation")
    st.markdown("Deterministic Level 1 geometric sanity checks and Level 2 manufacturing design rules.")

    spec = getattr(st.session_state, "current_spec", TubeSpec(length_mm=100.0, outer_diameter_mm=3.0, inner_diameter_mm=2.0))
    mesh, cad_res = getattr(st.session_state, "current_mesh", None), getattr(st.session_state, "current_cad_res", None)
    if mesh is None or cad_res is None:
        mesh, cad_res = build_tube(spec)

    mfg_process = st.selectbox("Target Manufacturing Process", ["Extrusion", "Injection Molding", "Additive (SLA 3D Printing)", "CNC Micro-Machining"])
    report = run_full_validation(spec, cad_res, manufacturing_process=mfg_process)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        status_html = '<span class="status-pass">✓ PASSED</span>' if report.passed else '<span class="status-fail">✗ ISSUES</span>'
        st.markdown(f"**Status:** {status_html}", unsafe_allow_html=True)
    with col2:
        st.metric("Errors / Blockers", report.error_count)
    with col3:
        st.metric("Warnings", report.warning_count)
    with col4:
        st.metric("Wall Thickness", f"{report.wall_thickness_mm:.3f} mm" if report.wall_thickness_mm else "N/A")

    st.divider()
    st.subheader("Validation Rule Findings")

    if report.issues:
        issue_records = []
        for i in report.issues:
            issue_records.append({
                "Severity": i.severity.value,
                "Rule Code": i.code,
                "Message": i.message,
                "Parameter": i.parameter or "General",
                "Action": i.suggested_fix or "Review specification"
            })
        st.table(pd.DataFrame(issue_records))
    else:
        st.success("✓ All Level 1 geometric checks and Level 2 manufacturing constraints passed without issues.")


# -------------------------------------------------------------
# TAB 4: MATERIALS ENGINE
# -------------------------------------------------------------
elif app_mode == "🧪 Materials Engine":
    st.header("🧪 Medical Materials Recommendation & Ranking Engine")
    st.markdown("Deterministic multi-factor material evaluation based on mechanical requirements, process methods, and ISO 10993 provenance.")

    col_req, col_rank = st.columns([1.1, 1.9])
    with col_req:
        st.subheader("Engineering Filters")
        min_tensile = st.slider("Min Tensile Strength (MPa)", 0, 1000, 20, step=5)
        flex_pref = st.selectbox("Flexibility Profile", ["any", "rigid", "semi_rigid", "flexible", "elastomeric"])
        steril_pref = st.selectbox("Required Sterilization", ["Any", "EtO", "Gamma", "Autoclave", "E-beam", "VHP"])
        mfg_pref = st.selectbox("Preferred Process", ["Any", "Extrusion", "Injection Molding", "Machining", "Laser Cutting"])

        reqs = MaterialRequirements(
            minimum_tensile_strength_mpa=float(min_tensile) if min_tensile > 0 else None,
            flexibility_preference=flex_pref,
            required_sterilization_method=None if steril_pref == "Any" else steril_pref,
            preferred_manufacturing_method=None if mfg_pref == "Any" else mfg_pref
        )

    with col_rank:
        st.subheader("Candidate Rankings")
        scored_candidates = evaluate_and_rank_materials(reqs, db=st.session_state.db)

        rows = []
        for idx, c in enumerate(scored_candidates, 1):
            m = c.material
            rows.append({
                "Rank": f"#{idx}",
                "Material": m.name,
                "Fit": c.engineering_fit,
                "Score": f"{c.score * 100:.0f}%",
                "Tensile (MPa)": m.tensile_strength_mpa,
                "Modulus (MPa)": m.elastic_modulus_mpa,
                "Sterilization (EtO)": m.sterilization_compatibility.get("EtO", "Compatible")
            })

        df_cand = pd.DataFrame(rows)
        st.dataframe(df_cand, use_container_width=True, hide_index=True)

        if scored_candidates:
            top = scored_candidates[0]
            with st.expander(f"🔍 Inspect Top Match: {top.material.name}"):
                st.markdown(f"**Engineering Fit:** `{top.engineering_fit}` ({top.score * 100:.0f}% match)")
                st.markdown(f"**Matched Criteria:** {', '.join(top.matched_criteria) if top.matched_criteria else 'None'}")
                if top.unmatched_criteria:
                    st.markdown(f"**Unmatched Criteria:** {', '.join(top.unmatched_criteria)}")
                st.markdown(f"**Data Provenance:** {top.evidence_provenance}")
                st.info(f"**Regulatory Boundary:** {top.regulatory_disclaimer}")


# -------------------------------------------------------------
# TAB 5: ENGINEERING SIMULATION
# -------------------------------------------------------------
elif app_mode == "⚡ Engineering Simulation":
    st.header("⚡ Deterministic Engineering Simulation Studio")
    st.markdown("Physics-based calculators for pressure containment, column pushability, and fluid dispense forces.")

    sim_tab1, sim_tab2, sim_tab3 = st.tabs(["💥 Burst & Hoop Stress", "📐 Column Buckling", "💉 Syringe Dispense Force"])

    with sim_tab1:
        st.subheader("Lamé Cylinder Internal Pressure & Hoop Stress")
        sc1, sc2 = st.columns([1, 1])
        with sc1:
            tube_od = st.number_input("Tube Outer Diameter (mm)", value=3.0, min_value=0.5, max_value=20.0, key="sim_burst_od")
            tube_id = st.number_input("Tube Inner Diameter (mm)", value=2.0, min_value=0.3, max_value=tube_od - 0.1, key="sim_burst_id")
            pressure_bar = st.slider("Operating Internal Pressure (bar)", 1.0, 50.0, 10.0, step=0.5)
            
            all_mats = st.session_state.db.get_all_materials()
            mat_names = [m.name for m in all_mats]
            sel_mat_name = st.selectbox("Material Grade", mat_names, index=0)
            sel_mat = next(m for m in all_mats if m.name == sel_mat_name)

        with sc2:
            spec = TubeSpec(length_mm=100.0, outer_diameter_mm=tube_od, inner_diameter_mm=tube_id)
            sim = BurstPressureSimulator()
            res = sim.run(spec, sel_mat, operating_pressure_bar=pressure_bar)

            st.markdown(f"### Simulation Outcome: `{res.status}`")
            st.metric("Yield Safety Factor", f"{res.yield_safety_factor:.2f}")
            st.metric("Peak Hoop Stress (Bore)", f"{res.hoop_stress_mpa:.2f} MPa")
            st.metric("Theoretical Burst Pressure", f"{res.theoretical_burst_pressure_bar:.1f} bar")
            st.info(res.solver_notes)

    with sim_tab2:
        st.subheader("Euler Column Buckling & Pushability Analysis")
        bc1, bc2 = st.columns([1, 1])
        with bc1:
            cath_len = st.number_input("Catheter Working Length (mm)", value=150.0, min_value=20.0, max_value=2000.0, key="sim_buck_len")
            cath_od = st.number_input("Outer Diameter (mm)", value=2.0, min_value=0.4, max_value=15.0, key="sim_buck_od")
            cath_id = st.number_input("Inner Diameter (mm)", value=1.2, min_value=0.2, max_value=cath_od - 0.1, key="sim_buck_id")
            push_force = st.slider("Applied Axial Push Force (N)", 0.2, 10.0, 1.5, step=0.1)

        with bc2:
            cath_spec = TubeSpec(length_mm=cath_len, outer_diameter_mm=cath_od, inner_diameter_mm=cath_id)
            buck_sim = ColumnBucklingSimulator()
            buck_res = buck_sim.run(cath_spec, sel_mat, applied_push_force_n=push_force)

            st.markdown(f"### Buckling Assessment: `{buck_res.status}`")
            st.metric("Critical Buckling Load", f"{buck_res.critical_buckling_load_n:.2f} N ({buck_res.critical_buckling_load_gf:.1f} gf)")
            st.metric("Pushability Safety Factor", f"{buck_res.buckling_safety_factor:.2f}")
            st.info(buck_res.solver_notes)

    with sim_tab3:
        st.subheader("Syringe Hagen-Poiseuille Dispense Force")
        fc1, fc2 = st.columns([1, 1])
        with fc1:
            inj_b_id = st.number_input("Barrel Bore ID (mm)", value=14.0, min_value=3.0, max_value=50.0, key="sim_flow_bid")
            gauge = st.selectbox("Needle Gauge (G)", [18, 20, 21, 22, 23, 25, 27, 30], index=4)
            flow_rate = st.slider("Dispense Flow Rate (mL/s)", 0.05, 5.0, 0.5, step=0.05)
            viscosity = st.number_input("Fluid Dynamic Viscosity (cP)", value=1.0, min_value=0.5, max_value=100.0, step=0.5)

        with fc2:
            inj_spec = InjectorSpec(
                body_length_mm=80.0,
                body_outer_diameter_mm=inj_b_id + 2.0,
                body_inner_diameter_mm=inj_b_id,
                flange_width_mm=inj_b_id + 10.0
            )
            flow_sim = SyringeFlowSimulator()
            flow_res = flow_sim.run(inj_spec, flow_rate_ml_s=flow_rate, fluid_viscosity_cp=viscosity, needle_gauge=gauge)

            st.markdown(f"### Ergonomic Assessment: `{flow_res.status}`")
            st.metric("Total Thumb Actuation Force", f"{flow_res.total_thumb_force_n:.1f} N ({flow_res.total_thumb_force_kgf:.2f} kgf)")
            st.metric("Nozzle Pressure Drop", f"{flow_res.pressure_drop_nozzle_bar:.2f} bar")
            st.info(flow_res.ergonomic_assessment)


# -------------------------------------------------------------
# TAB 6: DESIGN HISTORY & DIFFS
# -------------------------------------------------------------
elif app_mode == "📜 Design History & Diffs":
    st.header("📜 Immutable Design Version History & Audit Log")
    st.markdown("Every parameter adjustment and CAD regeneration produces an immutable version record.")

    designs = st.session_state.storage.list_designs()
    if designs:
        sel_des = st.selectbox("Select Design", [d["design_id"] for d in designs])
        history = st.session_state.storage.get_design_history(sel_des)

        st.subheader("Version Tree")
        v_list = [f"Version {h['version_number']} ({h['created_at_utc']})" for h in history]
        st.write(pd.DataFrame([
            {
                "Version": f"v{h['version_number']}",
                "Device": h["device_type"],
                "Created (UTC)": h["created_at_utc"],
                "Prompt / Action": h["user_prompt"]
            }
            for h in history
        ]))

        if len(history) >= 2:
            st.divider()
            st.subheader("Version Diff Comparison")
            c1, c2 = st.columns(2)
            with c1:
                va_idx = st.selectbox("Base Version", range(len(history)), index=0, format_func=lambda x: f"v{history[x]['version_number']}")
            with c2:
                vb_idx = st.selectbox("Comparison Version", range(len(history)), index=len(history)-1, format_func=lambda x: f"v{history[x]['version_number']}")

            diff = VersionComparator.compute_diff(history[va_idx], history[vb_idx])
            st.markdown(f"**Changed Parameters:** `{diff['changed_parameters_count']}`")
            if diff["differences"]:
                st.json(diff["differences"])
            else:
                st.info("No parameter differences between selected versions.")
    else:
        st.info("No saved designs in SQLite storage yet. Modify parameters in the Workbench and click 'Save as Immutable Version'.")


# -------------------------------------------------------------
# TAB 7: CONTROLLED EXPORT CENTER
# -------------------------------------------------------------
elif app_mode == "📦 Controlled Export Center":
    st.header("📦 Controlled Design Export Center")
    st.markdown("Generate and download authoritative STEP models, STL previews, design JSON specifications, and engineering reports.")

    spec = getattr(st.session_state, "current_spec", TubeSpec(length_mm=100.0, outer_diameter_mm=3.0, inner_diameter_mm=2.0))
    mesh, cad_res = getattr(st.session_state, "current_mesh", None), getattr(st.session_state, "current_cad_res", None)
    if mesh is None or cad_res is None:
        mesh, cad_res = build_tube(spec)

    st.markdown("### Export Artifact Bundle")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Authoritative Deliverables:**
        - `model.step` — ISO 10303-21 standard CAD B-Rep interchange file
        - `preview.stl` — Watertight triangulated surface mesh for 3D printing & viewer
        - `specification.json` — Immutable parametric dimensions and units
        - `report.md` — Comprehensive engineering analysis & validation report
        """)

    with col2:
        st.warning("⚠️ Export gate: Please confirm that this export is for engineering design prototyping and has not been approved for clinical or patient use.")
        confirm_export = st.checkbox("I acknowledge the Medical Device & Safety Boundary Notice")

    if confirm_export:
        design_id = st.session_state.current_design_id
        version = st.session_state.current_version

        val_rep = run_full_validation(spec, cad_res)
        bundle_paths = export_design_package(
            mesh=mesh,
            cad_result=cad_res,
            spec_dict=spec.model_dump(),
            validation_dict=val_rep.model_dump(),
            design_id=design_id,
            version=version
        )

        st.success(f"✓ Export package generated in: `{bundle_paths['package_directory']}`")

        c1, c2, c3 = st.columns(3)
        with c1:
            st.download_button(
                "📥 Download STEP CAD (.step)",
                data=Path(bundle_paths["step_file"]).read_bytes(),
                file_name=Path(bundle_paths["step_file"]).name,
                mime="application/step",
                use_container_width=True
            )
        with c2:
            st.download_button(
                "📥 Download STL Mesh (.stl)",
                data=Path(bundle_paths["stl_file"]).read_bytes(),
                file_name=Path(bundle_paths["stl_file"]).name,
                mime="application/sla",
                use_container_width=True
            )
        with c3:
            report_content = generate_engineering_report(
                design_id=design_id,
                version=version,
                spec=spec,
                cad_result=cad_res,
                validation_report=val_rep
            )
            st.download_button(
                "📥 Download Engineering Report (.md)",
                data=report_content,
                file_name=f"{design_id}_v{version}_report.md",
                mime="text/markdown",
                use_container_width=True
            )
