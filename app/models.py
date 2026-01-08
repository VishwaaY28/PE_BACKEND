from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Goal(Base):
    """Goal entity."""
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)

    # Relationships
    verticals = relationship("Vertical", back_populates="goal")

    def __repr__(self):
        return f"<Goal(id={self.id}, name={self.name})>"


class Vertical(Base):
    """Vertical entity."""
    __tablename__ = "verticals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=False)

    # Relationships
    goal = relationship("Goal", back_populates="verticals")
    sub_verticals = relationship("SubVertical", back_populates="vertical")

    def __repr__(self):
        return f"<Vertical(id={self.id}, name={self.name})>"


class SubVertical(Base):
    """Sub-Vertical entity."""
    __tablename__ = "sub_verticals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    vertical_id = Column(Integer, ForeignKey("verticals.id"), nullable=False)

    # Relationships
    vertical = relationship("Vertical", back_populates="sub_verticals")
    capabilities = relationship("Capability", back_populates="sub_vertical")

    def __repr__(self):
        return f"<SubVertical(id={self.id}, name={self.name})>"


class Capability(Base):
    """Capability entity."""
    __tablename__ = "capabilities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    sub_vertical_id = Column(Integer, ForeignKey("sub_verticals.id"), nullable=False)

    # Relationships
    sub_vertical = relationship("SubVertical", back_populates="capabilities")
    processes = relationship("Process", back_populates="capability")

    def __repr__(self):
        return f"<Capability(id={self.id}, name={self.name})>"


class Process(Base):
    """Process entity."""
    __tablename__ = "processes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    capability_id = Column(Integer, ForeignKey("capabilities.id"), nullable=False)
    process_level_id = Column(Integer, ForeignKey("process_levels.id"), nullable=True)
    process_category_id = Column(Integer, ForeignKey("process_categories.id"), nullable=True)

    # Relationships
    capability = relationship("Capability", back_populates="processes")
    process_level = relationship("ProcessLevel", back_populates="processes")
    process_category = relationship("ProcessCategory", back_populates="processes")
    sub_processes = relationship("SubProcess", back_populates="process")

    def __repr__(self):
        return f"<Process(id={self.id}, name={self.name})>"


class ProcessLevel(Base):
    """Process level entity."""
    __tablename__ = "process_levels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)

    # Relationships
    processes = relationship("Process", back_populates="process_level")

    def __repr__(self):
        return f"<ProcessLevel(id={self.id}, name={self.name})>"


class ProcessCategory(Base):
    """Process category entity."""
    __tablename__ = "process_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)

    # Relationships
    processes = relationship("Process", back_populates="process_category")

    def __repr__(self):
        return f"<ProcessCategory(id={self.id}, name={self.name})>"


class SubProcess(Base):
    """Sub-Process entity."""
    __tablename__ = "sub_processes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=True, index=True)
    description = Column(Text, nullable=True)
    process_id = Column(Integer, ForeignKey("processes.id"), nullable=True)

    # Relationships
    process = relationship("Process", back_populates="sub_processes")
    data_entities = relationship("DataEntity", back_populates="sub_process")

    def __repr__(self):
        return f"<SubProcess(id={self.id}, name={self.name})>"


class DataEntity(Base):
    """Data Entity."""
    __tablename__ = "data_entities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=True, index=True)
    sub_process_id = Column(Integer, ForeignKey("sub_processes.id"), nullable=True)

    # Relationships
    sub_process = relationship("SubProcess", back_populates="data_entities")
    applications = relationship("Application", back_populates="data_entity")

    def __repr__(self):
        return f"<DataEntity(id={self.id}, name={self.name})>"


class Application(Base):
    """Application entity."""
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=True, index=True)
    data_entity_id = Column(Integer, ForeignKey("data_entities.id"), nullable=True)

    # Relationships
    data_entity = relationship("DataEntity", back_populates="applications")
    apis = relationship("API", back_populates="application")

    def __repr__(self):
        return f"<Application(id={self.id}, name={self.name})>"


class API(Base):
    """API entity."""
    __tablename__ = "apis"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=True, index=True)
    assumption = Column(String(255), nullable=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=True)

    # Relationships
    application = relationship("Application", back_populates="apis")

    def __repr__(self):
        return f"<API(id={self.id}, name={self.name})>"
