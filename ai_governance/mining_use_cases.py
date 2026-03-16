"""Mining & extractive industry AI-ML use case registry and best practices.

Provides a catalogue of AI-ML use cases relevant to companies like Ma'aden
(Saudi Arabian Mining Company), covering:
- Predictive maintenance for mining equipment
- Ore grade optimization using ML algorithms
- Safety incident prediction and prevention
- Environmental/ESG monitoring with AI
- Energy management and process optimization
- Autonomous systems governance

Also includes best practices, standards, and policies for AI adoption
in the extractive industry context.
"""

from .models import AIUseCase, RiskLevel, UseCaseStatus


def get_mining_use_case_catalogue() -> list[AIUseCase]:
    """Return a catalogue of standard AI-ML use cases for mining operations.

    These represent common high-value use cases in the extractive industry
    that a Senior Specialist in Data Science and AI would evaluate, pilot,
    and deploy.
    """
    return [
        AIUseCase(
            use_case_id="MN-UC-001",
            name="Predictive Maintenance for SAG/Ball Mills",
            description=(
                "ML-based predictive maintenance system for semi-autogenous grinding (SAG) "
                "and ball mills, using vibration sensors, temperature data, and operational "
                "parameters to predict failures 7-14 days in advance."
            ),
            business_unit="Processing Plant",
            category="predictive_maintenance",
            status=UseCaseStatus.PILOTING,
            risk_level=RiskLevel.MODERATE,
            ai_techniques=["random_forest", "gradient_boosting", "time_series_anomaly_detection"],
            data_sources=["vibration_sensors", "scada_system", "maintenance_logs", "operational_parameters"],
            expected_benefit=(
                "Cost reduction of 15-25% in unplanned downtime; efficiency improvement "
                "in maintenance scheduling; safety improvement by preventing catastrophic failures."
            ),
            governance_controls=["D5-C01", "D5-C03", "D6-C01"],
        ),
        AIUseCase(
            use_case_id="MN-UC-002",
            name="Ore Grade Prediction & Blast Optimization",
            description=(
                "AI model to predict ore grade distribution from drill-hole data and "
                "geological surveys, enabling optimized blast patterns and selective "
                "mining to maximize recovery rates."
            ),
            business_unit="Mining Operations",
            category="process_optimization",
            status=UseCaseStatus.EVALUATING,
            risk_level=RiskLevel.MODERATE,
            ai_techniques=["neural_network", "kriging", "ensemble_methods"],
            data_sources=["drill_hole_assays", "geological_surveys", "blast_logs", "gps_fleet_data"],
            expected_benefit=(
                "Optimization of ore recovery by 5-10%; reduction in dilution and ore loss; "
                "cost reduction through targeted blasting."
            ),
            governance_controls=["D5-C01", "D5-C04"],
        ),
        AIUseCase(
            use_case_id="MN-UC-003",
            name="AI-Powered Safety Incident Prediction",
            description=(
                "ML system analyzing near-miss reports, environmental conditions, shift "
                "patterns, equipment status, and historical incident data to predict and "
                "prevent safety incidents in mining operations."
            ),
            business_unit="Safety & Sustainability",
            category="safety",
            status=UseCaseStatus.PROPOSED,
            risk_level=RiskLevel.HIGH,
            ai_techniques=["logistic_regression", "natural_language_processing", "bayesian_networks"],
            data_sources=[
                "incident_reports", "near_miss_database", "weather_data",
                "shift_schedules", "equipment_telemetry",
            ],
            expected_benefit=(
                "Safety improvement through early warning; 20-30% reduction in recordable "
                "incidents; compliance with Saudi Vision 2030 safety targets."
            ),
            governance_controls=["D3-C02", "D5-C02", "D5-C01", "D6-C01"],
        ),
        AIUseCase(
            use_case_id="MN-UC-004",
            name="AI-Based ESG Dashboard & Sustainability Reporting",
            description=(
                "Integrated AI dashboard aggregating environmental monitoring data (air "
                "quality, water usage, emissions), social metrics (workforce safety, community "
                "engagement), and governance KPIs for automated ESG reporting."
            ),
            business_unit="Sustainability, Safety & Innovation",
            category="environmental_monitoring",
            status=UseCaseStatus.EVALUATING,
            risk_level=RiskLevel.LOW,
            ai_techniques=["anomaly_detection", "time_series_forecasting", "nlp_report_generation"],
            data_sources=[
                "emissions_sensors", "water_quality_monitors", "energy_meters",
                "safety_database", "hr_systems", "community_feedback",
            ],
            expected_benefit=(
                "Sustainability compliance with Saudi Green Initiative targets; automated "
                "ESG reporting reducing manual effort by 60%; real-time anomaly detection "
                "for environmental exceedances."
            ),
            governance_controls=["ESG-E-01", "ESG-E-02", "ESG-G-01", "ESG-G-02", "ESG-I-03"],
        ),
        AIUseCase(
            use_case_id="MN-UC-005",
            name="Energy Consumption Optimization",
            description=(
                "AI system optimizing energy consumption across processing plants by "
                "predicting demand patterns, optimizing equipment scheduling, and "
                "recommending operational adjustments to reduce energy costs."
            ),
            business_unit="Processing Plant",
            category="energy_management",
            status=UseCaseStatus.PILOTING,
            risk_level=RiskLevel.LOW,
            ai_techniques=["reinforcement_learning", "time_series_forecasting", "optimization_algorithms"],
            data_sources=["energy_meters", "production_schedules", "weather_forecasts", "equipment_status"],
            expected_benefit=(
                "Cost reduction of 10-15% in energy costs; efficiency improvement in "
                "plant operations; sustainability through reduced carbon footprint."
            ),
            governance_controls=["ESG-E-04", "D5-C01"],
        ),
        AIUseCase(
            use_case_id="MN-UC-006",
            name="Autonomous Haul Truck Fleet Management",
            description=(
                "AI advisory system for autonomous and semi-autonomous haul truck fleet "
                "management, including route optimization, collision avoidance, and "
                "fuel efficiency optimization."
            ),
            business_unit="Mining Operations",
            category="autonomous_systems",
            status=UseCaseStatus.PROPOSED,
            risk_level=RiskLevel.CRITICAL,
            ai_techniques=["computer_vision", "reinforcement_learning", "path_planning", "sensor_fusion"],
            data_sources=["lidar_sensors", "gps_fleet_data", "mine_topology", "traffic_patterns"],
            expected_benefit=(
                "Automation of haulage operations; safety improvement by removing "
                "operators from hazardous zones; efficiency gains of 15-20% in haulage."
            ),
            governance_controls=["D3-C02", "D5-C02", "D5-C03", "D6-C01", "D6-C02"],
        ),
        AIUseCase(
            use_case_id="MN-UC-007",
            name="Water Treatment Process Optimization",
            description=(
                "ML-based optimization of water treatment and recycling processes in "
                "mining operations, predicting chemical dosing requirements and "
                "monitoring effluent quality in real-time."
            ),
            business_unit="Environmental Management",
            category="environmental_monitoring",
            status=UseCaseStatus.EVALUATING,
            risk_level=RiskLevel.MODERATE,
            ai_techniques=["regression_models", "anomaly_detection", "optimization_algorithms"],
            data_sources=["water_quality_sensors", "chemical_dosing_logs", "weather_data", "process_parameters"],
            expected_benefit=(
                "Compliance with environmental discharge regulations; cost reduction in "
                "chemical usage by 10-20%; sustainability through improved water recycling rates."
            ),
            governance_controls=["ESG-E-01", "ESG-E-03", "D5-C04"],
        ),
        AIUseCase(
            use_case_id="MN-UC-008",
            name="Mineral Exploration Target Identification",
            description=(
                "AI-driven analysis of geological, geophysical, and geochemical data to "
                "identify high-potential mineral exploration targets, reducing exploration "
                "costs and time-to-discovery."
            ),
            business_unit="Exploration",
            category="exploration",
            status=UseCaseStatus.PROPOSED,
            risk_level=RiskLevel.MODERATE,
            ai_techniques=["deep_learning", "spatial_analysis", "clustering", "transfer_learning"],
            data_sources=["geological_maps", "geophysical_surveys", "satellite_imagery", "drill_core_data"],
            expected_benefit=(
                "Predictive targeting improving discovery rate; cost reduction of 20-30% "
                "in exploration campaigns; competitive advantage in resource identification."
            ),
            governance_controls=["D5-C01", "D5-C04"],
        ),
    ]


# ---------------------------------------------------------------------------
# Best practices framework for AI adoption in extractive industry
# ---------------------------------------------------------------------------

def get_ai_adoption_best_practices() -> dict[str, list[dict[str, str]]]:
    """Return a structured best practices framework for AI adoption in mining.

    Organized by category, aligned with Technology CoE governance standards
    and Saudi Vision 2030 objectives.
    """
    return {
        "standards_and_policies": [
            {
                "id": "BP-SP-01",
                "title": "AI Ethics Policy for Mining Operations",
                "description": (
                    "Establish a formal AI ethics policy addressing transparency, "
                    "accountability, safety, and environmental responsibility specific "
                    "to mining and mineral processing contexts."
                ),
            },
            {
                "id": "BP-SP-02",
                "title": "Model Risk Management Framework",
                "description": (
                    "Implement a model risk management framework (aligned with SR 11-7 "
                    "principles) adapted for AI-ML models used in safety-critical mining "
                    "operations."
                ),
            },
            {
                "id": "BP-SP-03",
                "title": "Data Governance Standards for AI",
                "description": (
                    "Define data quality, lineage, access control, and retention standards "
                    "for data used in AI-ML applications, ensuring compliance with Saudi "
                    "data protection regulations."
                ),
            },
            {
                "id": "BP-SP-04",
                "title": "AI System Classification and Tiering",
                "description": (
                    "Classify AI systems into risk tiers (low/moderate/high/critical) with "
                    "corresponding governance requirements, testing protocols, and approval "
                    "processes."
                ),
            },
        ],
        "development_practices": [
            {
                "id": "BP-DP-01",
                "title": "MLOps Pipeline Standards",
                "description": (
                    "Establish CI/CD pipelines for ML models including automated testing, "
                    "validation, versioning, and deployment with rollback capabilities."
                ),
            },
            {
                "id": "BP-DP-02",
                "title": "Feature Engineering Documentation",
                "description": (
                    "Maintain comprehensive documentation of feature engineering decisions, "
                    "data transformations, and domain-specific knowledge codified in models."
                ),
            },
            {
                "id": "BP-DP-03",
                "title": "Cross-Functional Collaboration",
                "description": (
                    "Ensure data scientists collaborate with domain experts (geologists, "
                    "metallurgists, safety engineers) throughout the AI development lifecycle."
                ),
            },
        ],
        "monitoring_and_evaluation": [
            {
                "id": "BP-ME-01",
                "title": "Model Performance Monitoring",
                "description": (
                    "Implement continuous monitoring of deployed AI models for accuracy "
                    "degradation, data drift, and concept drift with automated alerting."
                ),
            },
            {
                "id": "BP-ME-02",
                "title": "Safety Impact Reviews",
                "description": (
                    "Conduct quarterly safety impact reviews for AI systems operating in "
                    "safety-critical mining environments."
                ),
            },
            {
                "id": "BP-ME-03",
                "title": "ESG Metrics Integration",
                "description": (
                    "Integrate AI system performance and impact metrics into ESG reporting "
                    "dashboards for stakeholder transparency."
                ),
            },
        ],
        "innovation_and_improvement": [
            {
                "id": "BP-II-01",
                "title": "AI Innovation Pipeline",
                "description": (
                    "Maintain a structured pipeline for evaluating, piloting, and scaling "
                    "new AI-ML use cases with stage-gate governance."
                ),
            },
            {
                "id": "BP-II-02",
                "title": "Industry Benchmarking",
                "description": (
                    "Regularly benchmark AI maturity against global mining peers and "
                    "emerging best practices from ICMM, IRMA, and similar bodies."
                ),
            },
            {
                "id": "BP-II-03",
                "title": "Knowledge Transfer and Training",
                "description": (
                    "Establish continuous learning programs to upskill operational staff "
                    "on AI tools and to keep the data science team current with advances "
                    "in the field."
                ),
            },
        ],
    }


def get_use_case_categories() -> dict[str, str]:
    """Return standard AI-ML use case categories for the extractive industry."""
    return {
        "predictive_maintenance": "Predicting equipment failures and optimizing maintenance schedules",
        "process_optimization": "Optimizing mineral processing, recovery rates, and throughput",
        "safety": "Predicting and preventing safety incidents in mining operations",
        "environmental_monitoring": "Monitoring emissions, water quality, and environmental compliance",
        "quality_control": "Automated quality inspection and grade control",
        "supply_chain": "Optimizing logistics, inventory, and supply chain operations",
        "workforce_analytics": "Workforce planning, training optimization, and productivity analysis",
        "energy_management": "Optimizing energy consumption and reducing carbon footprint",
        "exploration": "AI-driven mineral exploration and resource estimation",
        "autonomous_systems": "Autonomous vehicles, drones, and robotic systems in mining",
        "reporting": "Automated report generation and data visualization",
        "compliance": "Regulatory compliance monitoring and audit support",
    }
