import pandas as pd
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import (
    Goal, Vertical, SubVertical, Capability, Process, ProcessLevel,
    ProcessCategory, SubProcess, DataEntity, Application, API
)
import os


def seed_database():
    """
    Seed the database from CSV file.
    """
    # Read CSV file
    csv_path = os.path.join(os.path.dirname(__file__), "..", "EBRD_Compass.csv")
    
    if not os.path.exists(csv_path):
        print(f"CSV file not found at {csv_path}")
        return False

    df = pd.read_csv(csv_path)
    db: Session = SessionLocal()

    try:
        # Dictionary to cache created records (to avoid duplicates)
        goals_cache = {}
        verticals_cache = {}
        sub_verticals_cache = {}
        capabilities_cache = {}
        processes_cache = {}
        process_levels_cache = {}
        process_categories_cache = {}
        sub_processes_cache = {}
        data_entities_cache = {}
        applications_cache = {}

        for idx, row in df.iterrows():
            # Goal
            goal_name = row["Goal"]
            if goal_name not in goals_cache:
                goal = db.query(Goal).filter(Goal.name == goal_name).first()
                if not goal:
                    goal = Goal(name=goal_name)
                    db.add(goal)
                    db.flush()
                goals_cache[goal_name] = goal
            goal = goals_cache[goal_name]

            # Vertical
            vertical_name = row["Vertical"]
            if vertical_name not in verticals_cache:
                vertical = db.query(Vertical).filter(Vertical.name == vertical_name).first()
                if not vertical:
                    vertical = Vertical(name=vertical_name, goal_id=goal.id)
                    db.add(vertical)
                    db.flush()
                verticals_cache[vertical_name] = vertical
            vertical = verticals_cache[vertical_name]

            # Sub-Vertical
            sub_vertical_name = row["Sub-Vertical"]
            if sub_vertical_name not in sub_verticals_cache:
                sub_vertical = db.query(SubVertical).filter(
                    SubVertical.name == sub_vertical_name
                ).first()
                if not sub_vertical:
                    sub_vertical = SubVertical(name=sub_vertical_name, vertical_id=vertical.id)
                    db.add(sub_vertical)
                    db.flush()
                sub_verticals_cache[sub_vertical_name] = sub_vertical
            sub_vertical = sub_verticals_cache[sub_vertical_name]

            # Capability
            capability_name = row["Capability"]
            if capability_name not in capabilities_cache:
                capability = db.query(Capability).filter(
                    Capability.name == capability_name
                ).first()
                if not capability:
                    capability = Capability(
                        name=capability_name,
                        description=row.get("Capability Description", ""),
                        sub_vertical_id=sub_vertical.id,
                    )
                    db.add(capability)
                    db.flush()
                capabilities_cache[capability_name] = capability
            capability = capabilities_cache[capability_name]

            # Process
            process_name = row["Process"]
            process_key = f"{process_name}_{capability.id}"
            if process_key not in processes_cache:
                process = db.query(Process).filter(
                    Process.name == process_name,
                    Process.capability_id == capability.id
                ).first()
                if not process:
                    process = Process(
                        name=process_name,
                        description=row.get("Process Description", ""),
                        capability_id=capability.id,
                    )
                    db.add(process)
                    db.flush()
                processes_cache[process_key] = process
            process = processes_cache[process_key]

            # Process Level
            process_level_name = row.get("Process Level", "")
            if process_level_name and process_level_name not in process_levels_cache:
                process_level = db.query(ProcessLevel).filter(
                    ProcessLevel.level == process_level_name
                ).first()
                if not process_level:
                    process_level = ProcessLevel(level=process_level_name)
                    db.add(process_level)
                    db.flush()
                process_levels_cache[process_level_name] = process_level

            # Process Category
            process_category_name = row.get("Process Category", "")
            if process_category_name and process_category_name not in process_categories_cache:
                process_category = db.query(ProcessCategory).filter(
                    ProcessCategory.name == process_category_name
                ).first()
                if not process_category:
                    process_category = ProcessCategory(name=process_category_name)
                    db.add(process_category)
                    db.flush()
                process_categories_cache[process_category_name] = process_category

            # Sub-Process
            sub_process_name = row.get("Sub-Process", "")
            sub_process_key = f"{sub_process_name}_{process.id}"
            if sub_process_name and sub_process_key not in sub_processes_cache:
                sub_process = db.query(SubProcess).filter(
                    SubProcess.name == sub_process_name,
                    SubProcess.process_id == process.id
                ).first()
                if not sub_process:
                    process_level_id = process_levels_cache.get(
                        row.get("Process Level", "")
                    )
                    process_category_id = process_categories_cache.get(
                        row.get("Process Category", "")
                    )
                    
                    sub_process = SubProcess(
                        name=sub_process_name,
                        description=row.get("Sub-Process Description", ""),
                        process_id=process.id,
                        process_level_id=process_level_id.id if process_level_id else None,
                        process_category_id=process_category_id.id if process_category_id else None,
                    )
                    db.add(sub_process)
                    db.flush()
                sub_processes_cache[sub_process_key] = sub_process
            
            sub_process = sub_processes_cache.get(sub_process_key)

            # Data Entity
            data_entity_name = row.get("Data Entity", "")
            if data_entity_name and sub_process:
                data_entity_key = f"{data_entity_name}_{sub_process.id}"
                if data_entity_key not in data_entities_cache:
                    data_entity = db.query(DataEntity).filter(
                        DataEntity.name == data_entity_name,
                        DataEntity.sub_process_id == sub_process.id
                    ).first()
                    if not data_entity:
                        data_entity = DataEntity(
                            name=data_entity_name,
                            sub_process_id=sub_process.id,
                        )
                        db.add(data_entity)
                        db.flush()
                    data_entities_cache[data_entity_key] = data_entity
                data_entity = data_entities_cache[data_entity_key]

                # Applications (can be multiple, separated by semicolon)
                applications_str = row.get("Application", "")
                if applications_str:
                    app_names = [app.strip() for app in str(applications_str).split(";")]
                    for app_name in app_names:
                        if app_name:
                            app_key = f"{app_name}_{data_entity.id}"
                            if app_key not in applications_cache:
                                application = db.query(Application).filter(
                                    Application.name == app_name,
                                    Application.data_entity_id == data_entity.id
                                ).first()
                                if not application:
                                    application = Application(
                                        name=app_name,
                                        data_entity_id=data_entity.id,
                                    )
                                    db.add(application)
                                    db.flush()
                                applications_cache[app_key] = application
                            application = applications_cache[app_key]

                            # APIs (can be multiple, separated by semicolon)
                            apis_str = row.get("API (Assumption)", "")
                            if apis_str:
                                api_names = [api.strip() for api in str(apis_str).split(";")]
                                for api_name in api_names:
                                    if api_name:
                                        api = db.query(API).filter(
                                            API.name == api_name,
                                            API.application_id == application.id
                                        ).first()
                                        if not api:
                                            api = API(
                                                name=api_name,
                                                assumption="",
                                                application_id=application.id,
                                            )
                                            db.add(api)

        db.commit()
        print("Database seeded successfully!")
        return True

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def is_database_seeded():
    """
    Check if database has been seeded already.
    """
    db: Session = SessionLocal()
    try:
        count = db.query(Goal).count()
        return count > 0
    finally:
        db.close()
