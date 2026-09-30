"""
Generates an executive, formal 4-page academic progress report for EnviroMap-KG
Saved directly to C:\\Users\\Shreenithi\\Downloads\\enviromap_kg_progress_report_4pages.docx
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

def create_progress_report():
    doc = docx.Document()

    # Configure Margins for tight, elegant 4-page layout
    for section in doc.sections:
        section.top_margin = Inches(0.7)
        section.bottom_margin = Inches(0.7)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    NAVY = RGBColor(0, 51, 102)       # Primary Header (#003366)
    STEEL = RGBColor(51, 102, 153)    # Secondary Header (#336699)
    CHARCOAL = RGBColor(40, 40, 40)   # Body Text (#282828)
    DARK_RED = RGBColor(140, 20, 20)  # Callout/Metric (#8C1414)
    GRAY = RGBColor(100, 100, 100)

    def set_cell_background(cell, fill_hex):
        shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
        cell._tc.get_or_add_tcPr().append(shading)

    def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = OxmlElement('w:tcMar')
        for margin_name, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
            m = OxmlElement(f'w:{margin_name}')
            m.set(qn('w:w'), str(val))
            m.set(qn('w:type'), 'dxa')
            tcMar.append(m)
        tcPr.append(tcMar)

    def add_title(text, subtitle=""):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(16)
        run.font.name = "Arial"
        run.font.color.rgb = NAVY

        if subtitle:
            p2 = doc.add_paragraph()
            p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p2.paragraph_format.space_before = Pt(0)
            p2.paragraph_format.space_after = Pt(12)
            run2 = p2.add_run(subtitle)
            run2.font.size = Pt(10)
            run2.font.name = "Arial"
            run2.font.italic = True
            run2.font.color.rgb = STEEL

    def add_heading_1(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(10)
        h.paragraph_format.space_after = Pt(4)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.bold = True
        r.font.size = Pt(12)
        r.font.name = "Arial"
        r.font.color.rgb = NAVY

    def add_heading_2(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(6)
        h.paragraph_format.space_after = Pt(2)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.bold = True
        r.font.size = Pt(10.5)
        r.font.name = "Arial"
        r.font.color.rgb = STEEL

    def add_body(text, bold_prefix="", space_after=4):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.bold = True
            r_pre.font.size = Pt(9.5)
            r_pre.font.name = "Calibri"
            r_pre.font.color.rgb = CHARCOAL
        r = p.add_run(text)
        r.font.size = Pt(9.5)
        r.font.name = "Calibri"
        r.font.color.rgb = CHARCOAL
        return p

    def add_bullet(text, bold_prefix=""):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(2.5)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.bold = True
            r_pre.font.size = Pt(9.5)
            r_pre.font.name = "Calibri"
            r_pre.font.color.rgb = CHARCOAL
        r = p.add_run(text)
        r.font.size = Pt(9.5)
        r.font.name = "Calibri"
        r.font.color.rgb = CHARCOAL

    # =========================================================================
    # PAGE 1: PROJECT OVERVIEW, PROBLEM STATEMENT & INGRESS ARCHITECTURE
    # =========================================================================
    add_title("PROJECT PROGRESS REPORT: ENVIROMAP-KG", 
              "Autonomous Semantic Interoperability and Knowledge Graph Construction for City-Scale Environmental IoT")

    add_body("This document details the completed research, engineering modules, and empirical benchmarks achieved for EnviroMap-KG. The system eliminates manual schema engineering, rule-based dictionaries, and cloud-provider dependence, constructing standard W3C SOSA/SSN and ETSI SAREF Knowledge Graphs directly from live, heterogeneous sensor streams under a $0.00 cloud operational cost model.")

    add_heading_1("1. Problem Statement & Research Objectives")
    add_body("Environmental IoT deployments across smart cities and industrial facilities suffer from severe semantic and structural fragmentation:")
    add_bullet("Heterogeneous Protocols: Telemetry is siloed across MQTT, CoAP, oneM2M, OPC UA, HTTP, and AMQP without standardized schemas.", "1. Transport Silos: ")
    add_bullet("Cryptic Registers: Industrial hardware often outputs hex codes (e.g., REG_40102, REG_8820) or uninformative keys (val_1, aaaaa.i.xxx_y) requiring manual vendor datasheet lookup.", "2. Uninformative Identifiers: ")
    add_bullet("Relational Ingestion Bottleneck: Conventional relational SQL databases lock write-ahead logs (WAL) when ingesting city-scale data (> 100k ticks/sec), causing backpressure.", "3. Storage Contention: ")
    add_bullet("Zero-Human Autonomy: Achieving 100% autonomous discovery, alignment, reasoning, and validation with zero human configuration or mapping rules.", "4. Project Objective: ")

    add_heading_1("2. High-Level System Architecture & Ingress Tier")
    add_body("EnviroMap-KG implements an in-flight, two-speed architecture: high-frequency readings bypass heavy AI processing via an O(1) RAM fast-path (3 microseconds), while novel environments and cryptic sensors trigger an asynchronous 6-Agent AI pipeline (< 35 ms) that resolves the ontology mapping and updates the RAM cache in-place.")

    # Architecture Overview Table
    t_arch = doc.add_table(rows=1, cols=3)
    t_arch.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Ingress Protocol", "Gateway / Transport Mechanism", "Normalized Envelope Output"]
    for i, h in enumerate(headers):
        cell = t_arch.rows[0].cells[i]
        set_cell_background(cell, "003366")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(255, 255, 255)

    proto_rows = [
        ("MQTT", "EMQX / Mosquitto Broker (# wildcard subscription)", "Standard JSON Event Envelope in RAM"),
        ("CoAP", "Lightweight UDP datagram parser for 6LoWPAN", "Binary/CBOR unpacked to Float Observations"),
        ("oneM2M", "Eclipse OM2M Interworking Proxy (<cin> resources)", "SOSA FeatureOfInterest & Property linked"),
        ("OPC UA", "Python asyncua subscription client (NodeID monitor)", "Variable Node values mapped to SAREF Measurement"),
        ("HTTP", "FastAPI Asynchronous Ingestion Webhook Endpoint", "High-throughput JSON POST stream buffer"),
        ("AMQP", "RabbitMQ Consumer binding to exchange topics", "Dynamic routing key decomposed to Domain hints")
    ]
    for p_name, p_gw, p_out in proto_rows:
        row = t_arch.add_row()
        for idx, text in enumerate([p_name, p_gw, p_out]):
            c = row.cells[idx]
            set_cell_margins(c, 50, 50, 80, 80)
            if idx == 0:
                set_cell_background(c, "F5F8FA")
            p = c.paragraphs[0]
            r = p.add_run(text)
            r.font.size = Pt(8.0)
            r.font.name = "Calibri"
            r.font.color.rgb = CHARCOAL

    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    add_body("The normalized envelope ensures that the subsequent semantic engine operates in a 100% protocol-agnostic manner.", "Protocol Agnosticism: ")

    # =========================================================================
    # PAGE BREAK -> PAGE 2
    # =========================================================================
    doc.add_page_break()

    # =========================================================================
    # PAGE 2: THE 6-AGENT AUTONOMOUS SEMANTIC PIPELINE
    # =========================================================================
    add_title("PAGE 2: THE 6-AGENT AUTONOMOUS SEMANTIC PIPELINE", "Sequential Collaborative Neuro-Symbolic Agent Framework")

    add_body("When an unknown field or novel environment arrives, the system engages the 6-agent collaborative pipeline. Each agent is modeled as an autonomous micro-service executing a bounded semantic transformation task:")

    # Table of 6 Agents
    t_agents = doc.add_table(rows=1, cols=3)
    t_agents.alignment = WD_TABLE_ALIGNMENT.CENTER
    agent_headers = ["Agent Name", "Algorithmic Methodology", "Primary Output Artifact"]
    for i, h in enumerate(agent_headers):
        cell = t_agents.rows[0].cells[i]
        set_cell_background(cell, "003366")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(255, 255, 255)

    agent_data = [
        ("1. Streaming Discovery Agent", "Statistical profiling, waveform variance, and temporal gradient analysis.", "DiscoveryProfile with physics bounds"),
        ("2. Ontological Alignment Agent", "Dense embeddings (all-MiniLM-L6-v2) + ColBERT token-level MaxSim.", "Ranked AlignmentCandidates (Top-K)"),
        ("3. Schema Mapping Agent", "Context aggregation, UCUM/QUDT unit normalization, and FoI linkage.", "Canonical MappingRecord"),
        ("4. Hybrid Reasoning Agent", "Neuro-symbolic domain boosting (+0.20) and range plausibility verification.", "ReasoningDecision with confidence score"),
        ("5. Consistency Validation Agent", "W3C SHACL shape graph compliance and datatype compatibility checks.", "ValidationResult (VALID / INVALID)"),
        ("6. Continuous Learning Agent", "In-memory RAM cache promotion and persistent audit memory append.", "MappingMemoryEntry (Enables Fast-Path)")
    ]
    for a_name, a_meth, a_out in agent_data:
        row = t_agents.add_row()
        for idx, text in enumerate([a_name, a_meth, a_out]):
            c = row.cells[idx]
            set_cell_margins(c, 50, 50, 80, 80)
            if idx == 0:
                set_cell_background(c, "F5F8FA")
            p = c.paragraphs[0]
            r = p.add_run(text)
            r.font.size = Pt(8.0)
            r.font.name = "Calibri"
            r.font.color.rgb = CHARCOAL

    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    add_heading_1("Detailed Agent Functions & Logic")

    add_body("Extracts physical signal distributions from live streams without waiting for database writes. When cryptic register strings (e.g., REG_40102, REG_8820) appear, it passes sliding window metrics to the Physics Fingerprint Engine.", "Discovery Agent: ")

    add_body("Computes lexical similarity (RapidFuzz token set ratio) and semantic similarity using dense vector representations. Employs ColBERT late-interaction scoring to preserve token-level semantics: MaxSim(Q, D) = sum(max(E_qi * E_dj^T)).", "Alignment Agent: ")

    add_body("Binds the aligned concepts into standard W3C SOSA Observation structures, resolving unit ambiguities (e.g., converting mg/L or ppm into om:milligramPerLitre).", "Mapping Agent: ")

    add_body("Evaluates physical plausibility. For example, if a sensor reports water temperature of 25 C in a hydroponic tank, it boosts confidence (+0.20) while rejecting ambient air temperature concepts. If confidence falls below 0.85, it triggers local LLM advisory reasoning.", "Reasoning Agent: ")

    add_body("Enforces formal ontological constraints using W3C SHACL shape graphs. Validates that the property belongs to sosa:ObservableProperty, the value conforms to xsd:double, and the observation links to a valid Feature of Interest (sosa:hasFeatureOfInterest).", "Validation Agent: ")

    add_body("Updates the high-speed in-memory routing table: field::domain -> canonical_URI. Appends the decision to data/mapping_memory.json. Once committed, all future readings from this sensor execute in 3 microseconds on the fast-path.", "Learning Agent: ")

    # =========================================================================
    # PAGE BREAK -> PAGE 3
    # =========================================================================
    doc.add_page_break()

    # =========================================================================
    # PAGE 3: TARGETED ADVANCEMENTS, MATHEMATICAL ENGINES & BENCHMARKS
    # =========================================================================
    add_title("PAGE 3: MATHEMATICAL ADVANCEMENTS & LIVE BENCHMARKS", "Empirical Verification on Bare-Metal Ubuntu Server (192.168.0.21)")

    add_body("Seven targeted mathematical and algorithmic advancements were implemented, deployed, and validated on the departmental server (Ubuntu 24.04 LTS, Python 3.12, TimescaleDB):")

    # Table of Advancements
    t_adv = doc.add_table(rows=1, cols=4)
    t_adv.alignment = WD_TABLE_ALIGNMENT.CENTER
    adv_headers = ["Advancement", "Component File", "Core Algorithmic Technique", "Live Test Result"]
    for i, h in enumerate(adv_headers):
        cell = t_adv.rows[0].cells[i]
        set_cell_background(cell, "003366")
        set_cell_margins(cell, 80, 80, 80, 80)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(255, 255, 255)

    adv_data = [
        ("Adv. 1.1", "physics_fingerprint_engine.py", "Waveform variance (s^2) & dy/dt gradient profiling", "100% (Mapped REG_40102 to pH)"),
        ("Adv. 1.2", "reranker.py", "Micro-batched Cross-Encoder Candidate Reranking", "100% (Top-1 precision boost)"),
        ("Adv. 1.3", "dynamic_ontology_index.py", "Live RAM concept expansion without restart", "100% (Added Salinity & DO)"),
        ("Adv. 1.4", "streaming_discovery_agent.py", "Composite Multi-Vector ColBERT MaxSim", "100% (0.8863 MaxSim score)"),
        ("Adv. 2.1", "hybrid_storage_dispatcher.py", "TimescaleDB ticks + Jena Fuseki SOSA RDF", "100% (Dual-store synchronization)"),
        ("Adv. 2.2", "semantic_query_cache.py", "SHA-256 parameterized SPARQL graph cache", "100% (0.003 ms cache hit)"),
        ("Adv. 3.2", "sensor_drift_detector.py", "Rolling variance & dynamic Z-score tracking", "100% (Flagged drift in 12 ticks)"),
        ("Adv. 4.1", "streaming_discovery_agent.py", "Single-Pass SIMD Tensor Matrix Contraction", "100% (< 35 ms cold-start)"),
        ("Adv. 4.2", "cross_sensor_correlator.py", "Pearson cross-correlation (r=0.999) disambiguation", "100% (val_1 mapped to soil moist)"),
        ("Adv. 5.1/2", "qat_quantizer.py", "INT8 Quantization & AVX-512/VNNI hardware probe", "100% (3.88x inference speedup)")
    ]
    for aid, afile, atech, ares in adv_data:
        row = t_adv.add_row()
        for idx, text in enumerate([aid, afile, atech, ares]):
            c = row.cells[idx]
            set_cell_margins(c, 45, 45, 60, 60)
            if idx == 0:
                set_cell_background(c, "F5F8FA")
            p = c.paragraphs[0]
            r = p.add_run(text)
            r.font.size = Pt(7.8)
            r.font.name = "Calibri"
            r.font.color.rgb = CHARCOAL

    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    add_heading_1("Key Quantitative Benchmark Results")

    # Metrics Callout Table
    t_met = doc.add_table(rows=2, cols=3)
    t_met.alignment = WD_TABLE_ALIGNMENT.CENTER
    metrics_info = [
        ("TimescaleDB Bulk Ingest", "187,422 ticks / sec", "Tested live under continuous multi-client write"),
        ("Fast-Path Cache Hit", "0.003 ms (3 µs)", "In-memory RAM dictionary O(1) lookup"),
        ("Cold-Start Novelty Match", "< 35 ms", "Single-pass SIMD tensor matrix dot product"),
        ("Model Quantization", "3.88x Speedup", "INT8 ONNX runtime on commodity CPU"),
        ("Drift Detection Latency", "12 ticks (< 60s)", "Identifies sensor decalibration before corruption"),
        ("Cloud Infrastructure Cost", "$0.00 / month", "100% On-Premise bare-metal execution")
    ]
    for idx, (m_title, m_val, m_desc) in enumerate(metrics_info):
        r_idx = idx // 3
        c_idx = idx % 3
        cell = t_met.rows[r_idx].cells[c_idx]
        set_cell_background(cell, "F0F4F8")
        set_cell_margins(cell, 60, 60, 80, 80)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r1 = p.add_run(m_title + "\n")
        r1.font.size = Pt(8.0)
        r1.font.color.rgb = STEEL
        r2 = p.add_run(m_val + "\n")
        r2.bold = True
        r2.font.size = Pt(11.0)
        r2.font.color.rgb = DARK_RED
        r3 = p.add_run(m_desc)
        r3.font.size = Pt(7.5)
        r3.font.color.rgb = GRAY

    # =========================================================================
    # PAGE BREAK -> PAGE 4
    # =========================================================================
    doc.add_page_break()

    # =========================================================================
    # PAGE 4: ADAPTABILITY VALIDATION, DASHBOARD & NEXT MILESTONES
    # =========================================================================
    add_title("PAGE 4: ADAPTABILITY VALIDATION, DASHBOARD & MILESTONES", "Proof of Novel Environment Adaptation & Upcoming Pipeline Deployment")

    add_heading_1("1. Autonomous Adaptation to Novel Environments")
    add_body("To rigorously evaluate whether EnviroMap-KG can adapt when an unseen environment appears, a dedicated verification test (test_new_environment_adaptability.py) was executed. A novel domain—Smart Aquaculture—was introduced with zero prior rules or configuration:")
    add_bullet("The Dynamic Ontology Index ingested s4watr:Salinity and s4watr:DissolvedOxygen in RAM without restarting any service.", "Concept Expansion: ")
    add_bullet("Modbus register REG_8820 (Dissolved Oxygen) was evaluated solely from waveform variance (s^2 = 0.002) and gradient (dy/dt = 0.005), matching aquatic dissolved gas.", "Physics Inference: ")
    add_bullet("ColBERT late-interaction MaxSim achieved 0.8863 alignment confidence, promoting the mapping to VALID.", "High-Precision Match: ")
    add_bullet("Subsequent packets from REG_8820 immediately executed on the 3 µs fast-path.", "Fast-Path Transition: ")
    add_body("Result: 8 out of 8 automated tests passed (100% success rate), proving full adaptability.", "Test Suite Outcome: ")

    add_heading_1("2. Interactive Full-Stack Dashboard Implementation")
    add_body("A production-ready management dashboard was developed to monitor real-time interoperability:")
    add_bullet("React + Tailwind CSS with dark-mode theme, live telemetry cards, protocol health badges (MQTT, CoAP, oneM2M, OPC UA, HTTP, AMQP), and continuous throughput meters.", "Frontend Architecture: ")
    add_bullet("FastAPI service (fixed_api_main.py) exposing live TimescaleDB metrics, SPARQL endpoint proxying, pipeline execution states, and data acquisition triggers.", "Backend API: ")
    add_bullet("Interactive D3/SVG graph canvas rendering dynamic nodes for sosa:Sensor, sosa:Observation, sosa:ObservableProperty, and saref:UnitOfMeasure.", "Knowledge Graph Visualization: ")

    add_heading_1("3. Comprehensive Project Status & Upcoming Milestones")

    # Status Table
    t_status = doc.add_table(rows=1, cols=3)
    t_status.alignment = WD_TABLE_ALIGNMENT.CENTER
    s_headers = ["Project Work Package / Milestone", "Current State", "Verification / Deliverable"]
    for i, h in enumerate(s_headers):
        cell = t_status.rows[0].cells[i]
        set_cell_background(cell, "003366")
        set_cell_margins(cell, 80, 80, 80, 80)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(255, 255, 255)

    status_data = [
        ("WP1: Multi-Protocol Ingress Adapters", "100% Completed", "MQTT, CoAP, oneM2M, OPC UA, HTTP, AMQP normalized"),
        ("WP2: 6-Agent Semantic Pipeline", "100% Completed", "Discovery, Alignment, Mapping, Reasoning, Validation, Learning"),
        ("WP3: 7 Targeted Mathematical Advancements", "100% Completed", "All 7 passed live on 192.168.0.21 server"),
        ("WP4: Novel Domain Adaptability Suite", "100% Completed", "Verified on Smart Aquaculture domain (8/8 tests pass)"),
        ("WP5: Hybrid Dual-Store Ingestion", "100% Completed", "TimescaleDB (187k ticks/s) + Apache Jena Fuseki / RDFLib"),
        ("WP6: Interactive Web Dashboard & API", "100% Completed", "React visualizer + FastAPI SPARQL proxy service"),
        ("WP7: Distributed Kafka & EMQX Deployment", "Ready for Launch", "Docker Compose configuration & worker script drafted")
    ]
    for m_wp, m_st, m_ver in status_data:
        row = t_status.add_row()
        for idx, text in enumerate([m_wp, m_st, m_ver]):
            c = row.cells[idx]
            set_cell_margins(c, 45, 45, 60, 60)
            if idx == 0:
                set_cell_background(c, "F5F8FA")
            p = c.paragraphs[0]
            r = p.add_run(text)
            r.font.size = Pt(8.0)
            r.font.name = "Calibri"
            if "100% Completed" in text:
                r.bold = True
                r.font.color.rgb = RGBColor(0, 100, 0)
            elif "Ready" in text:
                r.bold = True
                r.font.color.rgb = STEEL
            else:
                r.font.color.rgb = CHARCOAL

    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    add_heading_2("Immediate Next Work: Apache Kafka & EMQX Broker Deployment")
    add_body("Having validated all in-flight semantic algorithms in RAM, the immediate next action is executing Docker Compose on server 192.168.0.21 to run Apache Kafka (KRaft mode) and EMQX 5.8. This will link real physical network brokers directly to our 6-agent semantic pipeline, completing the distributed city-scale deployment.")

    # Save to Downloads
    out_path = r"C:\Users\Shreenithi\Downloads\enviromap_kg_progress_report_4pages.docx"
    doc.save(out_path)
    print(f"Document successfully created at: {out_path}")

if __name__ == "__main__":
    create_progress_report()
