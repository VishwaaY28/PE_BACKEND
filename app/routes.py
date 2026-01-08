from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.database import get_db
from app.models import (
    Capability, Goal, Vertical, SubVertical, Process, SubProcess, 
    DataEntity, Application, API, ProcessLevel, ProcessCategory
)
from app.schemas import CapabilityDetailResponse, CapabilitySimpleResponse, ProcessResponse, SubProcessResponse, DataEntityResponse, ApplicationResponse, APIResponse
from typing import List

router = APIRouter(prefix="/api", tags=["pe-compass"])


@router.get("/capabilities", response_model=List[CapabilityDetailResponse])
def get_all_capabilities(db: Session = Depends(get_db)):
    """
    Get all capabilities with complete details.
    
    Returns all capabilities with their full hierarchy:
    - Capability details (name, description)
    - Goal, Vertical, and Sub-Vertical information
    - All associated processes with their sub-processes
    - Data entities, applications, and APIs
    """
    capabilities = db.query(Capability).all()
    if not capabilities:
        raise HTTPException(status_code=404, detail="No capabilities found")
    
    result = []
    for capability in capabilities:
        # Get related information
        sub_vertical = db.query(SubVertical).filter(
            SubVertical.id == capability.sub_vertical_id
        ).first()

        vertical = db.query(Vertical).filter(
            Vertical.id == sub_vertical.vertical_id
        ).first()

        goal = db.query(Goal).filter(
            Goal.id == vertical.goal_id
        ).first()

        # Get processes with related data
        processes = db.query(Process).filter(
            Process.capability_id == capability.id
        ).all()

        processes_data = []
        for process in processes:
            sub_processes = db.query(SubProcess).filter(
                SubProcess.process_id == process.id
            ).all()

            sub_processes_data = []
            for sub_process in sub_processes:
                data_entities = db.query(DataEntity).filter(
                    DataEntity.sub_process_id == sub_process.id
                ).all()

                data_entities_data = []
                for data_entity in data_entities:
                    applications = db.query(Application).filter(
                        Application.data_entity_id == data_entity.id
                    ).all()

                    applications_data = []
                    for application in applications:
                        apis = db.query(API).filter(
                            API.application_id == application.id
                        ).all()

                        apis_data = [
                            APIResponse(
                                id=api.id,
                                name=api.name,
                                assumption=api.assumption
                            )
                            for api in apis
                        ]

                        applications_data.append(
                            ApplicationResponse(
                                id=application.id,
                                name=application.name,
                                apis=apis_data
                            )
                        )

                    data_entities_data.append(
                        DataEntityResponse(
                            id=data_entity.id,
                            name=data_entity.name,
                            applications=applications_data
                        )
                    )

                process_level = None
                process_category = None
                if sub_process.process_level_id:
                    pl = db.query(ProcessLevel).filter(
                        ProcessLevel.id == sub_process.process_level_id
                    ).first()
                    process_level = pl.level if pl else None

                if sub_process.process_category_id:
                    pc = db.query(ProcessCategory).filter(
                        ProcessCategory.id == sub_process.process_category_id
                    ).first()
                    process_category = pc.name if pc else None

                sub_processes_data.append(
                    SubProcessResponse(
                        id=sub_process.id,
                        name=sub_process.name,
                        description=sub_process.description,
                        process_level=process_level,
                        process_category=process_category,
                        data_entities=data_entities_data
                    )
                )

            processes_data.append(
                ProcessResponse(
                    id=process.id,
                    name=process.name,
                    description=process.description,
                    sub_processes=sub_processes_data
                )
            )

        result.append(
            CapabilityDetailResponse(
                id=capability.id,
                name=capability.name,
                description=capability.description,
                goal=goal.name if goal else "",
                vertical=vertical.name if vertical else "",
                sub_vertical=sub_vertical.name if sub_vertical else "",
                processes=processes_data
            )
        )
    
    return result


@router.get("/capability/{capability_name}", response_model=CapabilityDetailResponse)
def get_capability_by_name(capability_name: str, db: Session = Depends(get_db)):
    """
    Get capability details by capability name.
    
    This endpoint returns comprehensive information about a capability including:
    - Capability name and description
    - Goal, Vertical, and Sub-Vertical information
    - All associated processes with their sub-processes
    - Data entities, applications, and APIs
    """
    # Query capability
    capability = db.query(Capability).filter(
        Capability.name == capability_name
    ).first()

    if not capability:
        raise HTTPException(
            status_code=404,
            detail=f"Capability '{capability_name}' not found"
        )

    # Get related information
    sub_vertical = db.query(SubVertical).filter(
        SubVertical.id == capability.sub_vertical_id
    ).first()

    vertical = db.query(Vertical).filter(
        Vertical.id == sub_vertical.vertical_id
    ).first()

    goal = db.query(Goal).filter(
        Goal.id == vertical.goal_id
    ).first()

    # Get processes with related data
    processes = db.query(Process).filter(
        Process.capability_id == capability.id
    ).all()

    processes_data = []
    for process in processes:
        sub_processes = db.query(SubProcess).filter(
            SubProcess.process_id == process.id
        ).all()

        sub_processes_data = []
        for sub_process in sub_processes:
            data_entities = db.query(DataEntity).filter(
                DataEntity.sub_process_id == sub_process.id
            ).all()

            data_entities_data = []
            for data_entity in data_entities:
                applications = db.query(Application).filter(
                    Application.data_entity_id == data_entity.id
                ).all()

                applications_data = []
                for application in applications:
                    apis = db.query(API).filter(
                        API.application_id == application.id
                    ).all()

                    apis_data = [
                        APIResponse(
                            id=api.id,
                            name=api.name,
                            assumption=api.assumption
                        )
                        for api in apis
                    ]

                    applications_data.append(
                        ApplicationResponse(
                            id=application.id,
                            name=application.name,
                            apis=apis_data
                        )
                    )

                data_entities_data.append(
                    DataEntityResponse(
                        id=data_entity.id,
                        name=data_entity.name,
                        applications=applications_data
                    )
                )

            process_level = None
            process_category = None
            if sub_process.process_level_id:
                pl = db.query(ProcessLevel).filter(
                    ProcessLevel.id == sub_process.process_level_id
                ).first()
                process_level = pl.level if pl else None

            if sub_process.process_category_id:
                pc = db.query(ProcessCategory).filter(
                    ProcessCategory.id == sub_process.process_category_id
                ).first()
                process_category = pc.name if pc else None

            sub_processes_data.append(
                SubProcessResponse(
                    id=sub_process.id,
                    name=sub_process.name,
                    description=sub_process.description,
                    process_level=process_level,
                    process_category=process_category,
                    data_entities=data_entities_data
                )
            )

        processes_data.append(
            ProcessResponse(
                id=process.id,
                name=process.name,
                description=process.description,
                sub_processes=sub_processes_data
            )
        )

    return CapabilityDetailResponse(
        id=capability.id,
        name=capability.name,
        description=capability.description,
        goal=goal.name if goal else "",
        vertical=vertical.name if vertical else "",
        sub_vertical=sub_vertical.name if sub_vertical else "",
        processes=processes_data
    )


@router.get("/capabilities/search", response_model=List[CapabilityDetailResponse])
def search_capabilities(keyword: str, db: Session = Depends(get_db)):
    """
    Search capabilities by keyword in name or description.
    
    Returns all matching capabilities with their full hierarchy:
    - Capability details (name, description)
    - Goal, Vertical, and Sub-Vertical information
    - All associated processes with their sub-processes
    - Data entities, applications, and APIs
    """
    from sqlalchemy import or_
    
    capabilities = db.query(Capability).filter(
        or_(
            Capability.name.ilike(f"%{keyword}%"),
            Capability.description.ilike(f"%{keyword}%")
        )
    ).all()

    if not capabilities:
        raise HTTPException(
            status_code=404,
            detail=f"No capabilities found matching keyword '{keyword}'"
        )

    result = []
    for capability in capabilities:
        # Get related information
        sub_vertical = db.query(SubVertical).filter(
            SubVertical.id == capability.sub_vertical_id
        ).first()

        vertical = db.query(Vertical).filter(
            Vertical.id == sub_vertical.vertical_id
        ).first()

        goal = db.query(Goal).filter(
            Goal.id == vertical.goal_id
        ).first()

        # Get processes with related data
        processes = db.query(Process).filter(
            Process.capability_id == capability.id
        ).all()

        processes_data = []
        for process in processes:
            sub_processes = db.query(SubProcess).filter(
                SubProcess.process_id == process.id
            ).all()

            sub_processes_data = []
            for sub_process in sub_processes:
                data_entities = db.query(DataEntity).filter(
                    DataEntity.sub_process_id == sub_process.id
                ).all()

                data_entities_data = []
                for data_entity in data_entities:
                    applications = db.query(Application).filter(
                        Application.data_entity_id == data_entity.id
                    ).all()

                    applications_data = []
                    for application in applications:
                        apis = db.query(API).filter(
                            API.application_id == application.id
                        ).all()

                        apis_data = [
                            APIResponse(
                                id=api.id,
                                name=api.name,
                                assumption=api.assumption
                            )
                            for api in apis
                        ]

                        applications_data.append(
                            ApplicationResponse(
                                id=application.id,
                                name=application.name,
                                apis=apis_data
                            )
                        )

                    data_entities_data.append(
                        DataEntityResponse(
                            id=data_entity.id,
                            name=data_entity.name,
                            applications=applications_data
                        )
                    )

                process_level = None
                process_category = None
                if sub_process.process_level_id:
                    pl = db.query(ProcessLevel).filter(
                        ProcessLevel.id == sub_process.process_level_id
                    ).first()
                    process_level = pl.level if pl else None

                if sub_process.process_category_id:
                    pc = db.query(ProcessCategory).filter(
                        ProcessCategory.id == sub_process.process_category_id
                    ).first()
                    process_category = pc.name if pc else None

                sub_processes_data.append(
                    SubProcessResponse(
                        id=sub_process.id,
                        name=sub_process.name,
                        description=sub_process.description,
                        process_level=process_level,
                        process_category=process_category,
                        data_entities=data_entities_data
                    )
                )

            processes_data.append(
                ProcessResponse(
                    id=process.id,
                    name=process.name,
                    description=process.description,
                    sub_processes=sub_processes_data
                )
            )

        result.append(
            CapabilityDetailResponse(
                id=capability.id,
                name=capability.name,
                description=capability.description,
                goal=goal.name if goal else "",
                vertical=vertical.name if vertical else "",
                sub_vertical=sub_vertical.name if sub_vertical else "",
                processes=processes_data
            )
        )

    return result


@router.get("/health")
def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok", "message": "PE Compass API is running"}
