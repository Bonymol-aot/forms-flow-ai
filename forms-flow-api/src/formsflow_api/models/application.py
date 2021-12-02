"""This manages Application submission Data."""

from __future__ import annotations

from sqlalchemy import and_, func, or_, distinct

from formsflow_api.models.audit_mixin import AuditDateTimeMixin, AuditUserMixin
from formsflow_api.models.base_model import BaseModel
from formsflow_api.models.db import db
from formsflow_api.models.form_process_mapper import FormProcessMapper
from formsflow_api.utils import ApplicationSortingParameters


class Application(AuditDateTimeMixin, AuditUserMixin, BaseModel, db.Model):
    """This class manages application against each form."""

    id = db.Column(db.Integer, primary_key=True)
    application_name = db.Column(db.String(100), nullable=False)
    application_status = db.Column(db.String(100), nullable=False)
    form_process_mapper_id = db.Column(
        db.Integer, db.ForeignKey("form_process_mapper.id"), nullable=False
    )
    form_url = db.Column(db.String(500), nullable=True)
    process_instance_id = db.Column(db.String(100), nullable=True)
    revision_no = db.Column(db.Integer, nullable=False)  # set 1 now

    @classmethod
    def create_from_dict(cls, application_info: dict) -> Application:
        """Create new application."""
        if application_info:
            application = Application()
            application.application_name = application_info["application_name"]
            application.application_status = application_info["application_status"]
            application.form_process_mapper_id = application_info[
                "form_process_mapper_id"
            ]
            application.form_url = application_info["form_url"]
            application.revision_no = 1  # application_info['revision_no']
            application.created_by = application_info["created_by"]
            application.save()
            return application
        return None

    def update(self, mapper_info: dict):
        """Update application."""
        self.update_from_dict(
            [
                "application_name",
                "application_status",
                "form_url",
                "form_process_mapper_id",
                "process_instance_id",
                "revision_no",
                "modified_by",
            ],
            mapper_info,
        )
        self.commit()

    @classmethod
    def find_by_id(cls, application_id: int) -> Application:
        """Find application that matches the provided id."""
        return cls.query.filter_by(id=application_id).first()

    @classmethod
    def find_all_application_status(cls):
        """Find all application status"""
        return cls.query.distinct(Application.application_status).all()

    @classmethod
    def find_by_ids(cls, application_ids) -> Application:
        """Find application that matches the provided id."""
        return cls.query.filter(cls.id.in_(application_ids)).order_by(
            Application.id.desc()
        )

    @classmethod
    def find_all(cls, page_no: int, limit: int) -> Application:
        """Fetch all application."""
        if page_no == 0:
            return cls.query.order_by(Application.id.desc()).all()
        else:
            return (
                cls.query.order_by(Application.id.desc())
                .paginate(page_no, limit, False)
                .items
            )

    @classmethod
    def find_all_by_user(
        cls,
        user_id: str,
        page_no: int,
        limit: int,
        order_by: str,
        application_id: int,
        application_name: str,
        application_status: str,
        created_by: str,
        created_from: str,
        created_to: str,
        modified_from: str,
        modified_to: str,
        sort_order: str,
    ) -> Application:
        """Fetch applications list based on searching parameters for Non-reviewer"""
        if application_id:
            return (
                cls.query.filter(Application.id == application_id)
                .filter(Application.created_by == user_id)
                .paginate(page_no, limit)
                .items
            )
        elif application_name and application_status and modified_from and modified_to:
            return (
                cls.query.filter(
                    Application.application_name.like(f"{application_name}%")
                )
                .filter(
                    Application.application_status.like(f"{application_status}%")
                )
                .filter(
                    and_(
                        func.date(Application.modified) >= modified_from,
                        func.date(Application.modified) <= modified_to,
                    )
                )
                .filter(Application.created_by == user_id)
                .paginate(page_no, limit)
                .items
            )
        elif application_name and application_status:
            return (
                cls.query.filter(
                    Application.application_name.like(f"{application_name}%")
                )
                .filter(
                    Application.application_status.like(f"{application_status}%")
                )
                .filter(Application.created_by == user_id)
                .paginate(page_no, limit)
                .items
            )
        elif application_name and modified_from and modified_to:
            return (
                cls.query.filter(
                    Application.application_name.like(f"{application_name}%")
                )
                .filter(
                    and_(
                        func.date(Application.modified) >= modified_from,
                        func.date(Application.modified) <= modified_to,
                    )
                )
                .filter(Application.created_by == user_id)
                .paginate(page_no, limit)
                .items
            )
        elif application_status and modified_from and modified_to:
            return (
                cls.query.filter(
                    Application.application_status.like(f"{application_status}%")
                )
                .filter(
                    and_(
                        func.date(Application.modified) >= modified_from,
                        func.date(Application.modified) <= modified_to,
                    )
                )
                .filter(Application.created_by == user_id)
                .paginate(page_no, limit)
                .items
            )
        elif application_name:
            return (
                cls.query.filter(
                    Application.application_name.like(f"{application_name}%")
                )
                .filter(Application.created_by == user_id)
                .paginate(page_no, limit)
                .items
            )
        elif application_status:
            return (
                cls.query.filter(
                    Application.application_status.like(f"{application_status}%")
                )
                .filter(Application.created_by == user_id)
                .paginate(page_no, limit)
                .items
            )
        elif modified_from and modified_to:
            return (
                cls.query.filter(
                    and_(
                        func.date(Application.modified) >= modified_from,
                        func.date(Application.modified) <= modified_to,
                    )
                )
                .filter(Application.created_by == user_id)
                .paginate(page_no, limit)
                .items
            )
        elif created_by:
            return (
                cls.query.filter(Application.created_by == created_by)
                .filter(Application.created_by == user_id)
                .paginate(page_no, limit)
                .items
            )
        elif created_from and created_to:
            return (
                cls.query.filter(
                    and_(
                        func.date(Application.created) >= created_from,
                        func.date(Application.created) <= created_to,
                    )
                )
                .filter(Application.created_by == user_id)
                .paginate(page_no, limit)
                .items
            )

        if order_by == ApplicationSortingParameters.Id and sort_order == "asc":
            return (
                cls.query.order_by(Application.id.asc())
                .filter(Application.created_by == user_id)
                .paginate(page_no, limit)
                .items
            )
        elif order_by == ApplicationSortingParameters.Id and sort_order == "desc":
            return (
                cls.query.order_by(Application.id.desc())
                .filter(Application.created_by == user_id)
                .paginate(page_no, limit)
                .items
            )
        elif order_by == ApplicationSortingParameters.Created:
            return (
                cls.query.order_by(Application.created)
                .filter(Application.created_by == user_id)
                .paginate(page_no, limit)
                .items
            )

        elif order_by == ApplicationSortingParameters.Name and sort_order == "asc":
            return (
                cls.query.order_by(Application.application_name.asc())
                .filter(Application.created_by == user_id)
                .paginate(page_no, limit)
                .items
            )
        elif order_by == ApplicationSortingParameters.Name and sort_order == "desc":
            return (
                cls.query.order_by(Application.application_name.desc())
                .filter(Application.created_by == user_id)
                .paginate(page_no, limit)
                .items
            )
        elif order_by == ApplicationSortingParameters.Status:
            return (
                cls.query.order_by(Application.application_status.asc())
                .filter(Application.created_by == user_id)
                .paginate(page_no, limit)
                .items
            )
        elif order_by == ApplicationSortingParameters.Modified:
            return (
                cls.query.order_by(Application.modified.asc())
                .filter(Application.created_by == user_id)
                .paginate(page_no, limit)
                .items
            )

        if page_no == 0:
            return cls.query.filter(Application.created_by == user_id).order_by(
                Application.id.desc()
            )
        else:
            return (
                cls.query.filter(Application.created_by == user_id)
                .order_by(Application.id.desc())
                .paginate(page_no, limit)
                .items
            )

    @classmethod
    def find_all_by_user_group(cls, user_id: str, page_no: int, limit: int):
        if page_no == 0:
            return cls.query.filter(Application.created_by == user_id).order_by(
                Application.id.desc()
            )
        else:
            return (
                cls.query.filter(Application.created_by == user_id)
                .order_by(Application.id.desc())
                .paginate(page_no, limit, False)
                .items
            )

    @classmethod
    def find_id_by_user(cls, application_id: int, user_id: str) -> Application:
        """Find application that matches the provided id."""
        return cls.query.filter(
            and_(Application.id == application_id, Application.created_by == user_id)
        ).one_or_none()

    @classmethod
    def find_all_by_user_count(cls, user_id: str) -> Application:
        """Fetch all application."""
        return cls.query.filter(Application.created_by == user_id).count()

    @classmethod
    def find_by_form_id(cls, form_id, page_no: int, limit: int):
        if page_no == 0:
            return cls.query.filter(
                Application.form_url.like("%" + form_id + "%")
            ).order_by(Application.id.desc())
        else:
            return (
                cls.query.filter(Application.form_url.like("%" + form_id + "%"))
                .order_by(Application.id.desc())
                .paginate(page_no, limit, False)
                .items
            )

    @classmethod
    def find_by_form_names(
        cls,
        form_names: str,
        application_id: int,
        created_from: str,
        created_to: str,
        modified_from: str,
        modified_to: str,
        application_name: str,
        application_status: str,
        created_by: str,
        page_no: int,
        limit: int,
        order_by: str,
        sort_order: str,
    ):
        """Fetch applications list based on searching parameters for Reviewer"""
        if application_id:
            return (
                cls.query.filter(Application.id == application_id)
                .filter(Application.application_name.in_(form_names))
                .paginate(page_no, limit)
                .items
            )
        elif application_name and application_status and modified_from and modified_to:
            return (
                cls.query.filter(
                    Application.application_name.like(f"{application_name}%")
                )
                .filter(
                    Application.application_status.like(f"{application_status}%")
                )
                .filter(
                    and_(
                        func.date(Application.modified) >= modified_from,
                        func.date(Application.modified) <= modified_to,
                    )
                )
                .filter(Application.application_name.in_(form_names))
                .paginate(page_no, limit)
                .items
            )
        elif application_name and application_status:
            return (
                cls.query.filter(
                    Application.application_name.like(f"{application_name}%")
                )
                .filter(
                    Application.application_status.like(f"{application_status}%")
                )
                .filter(Application.application_name.in_(form_names))
                .paginate(page_no, limit)
                .items
            )
        elif application_name and modified_from and modified_to:
            return (
                cls.query.filter(
                    Application.application_name.like(f"{application_name}%")
                )
                .filter(
                    and_(
                        func.date(Application.modified) >= modified_from,
                        func.date(Application.modified) <= modified_to,
                    )
                )
                .filter(Application.application_name.in_(form_names))
                .paginate(page_no, limit)
                .items
            )
        elif application_status and modified_from and modified_to:
            return (
                cls.query.filter(
                    Application.application_status.like(f"{application_status}%")
                )
                .filter(
                    and_(
                        func.date(Application.modified) >= modified_from,
                        func.date(Application.modified) <= modified_to,
                    )
                )
                .filter(Application.application_name.in_(form_names))
                .paginate(page_no, limit)
                .items
            )
        elif application_name:
            return (
                cls.query.filter(
                    Application.application_name.like(f"{application_name}%")
                )
                .filter(Application.application_name.in_(form_names))
                .paginate(page_no, limit)
                .items
            )
        elif application_status:
            return (
                cls.query.filter(
                    Application.application_status.like(f"{application_status}%")
                )
                .filter(Application.application_name.in_(form_names))
                .paginate(page_no, limit)
                .items
            )
        elif modified_from and modified_to:
            return (
                cls.query.filter(
                    and_(
                        func.date(Application.modified) >= modified_from,
                        func.date(Application.modified) <= modified_to,
                    )
                )
                .filter(Application.application_name.in_(form_names))
                .paginate(page_no, limit)
                .items
            )
        elif created_by:
            return (
                cls.query.filter(Application.created_by == created_by)
                .filter(Application.application_name.in_(form_names))
                .paginate(page_no, limit)
                .items
            )
        elif created_from and created_to:
            return (
                cls.query.filter(
                    and_(
                        func.date(Application.created) >= created_from,
                        func.date(Application.created) <= created_to,
                    )
                )
                .filter(Application.application_name.in_(form_names))
                .paginate(page_no, limit)
                .items
            )

        if order_by == ApplicationSortingParameters.Id and sort_order == "asc":
            return (
                cls.query.order_by(Application.id.asc())
                .filter(Application.application_name.in_(form_names))
                .paginate(page_no, limit)
                .items
            )
        elif order_by == ApplicationSortingParameters.Id and sort_order == "desc":
            return (
                cls.query.order_by(Application.id.desc())
                .filter(Application.application_name.in_(form_names))
                .paginate(page_no, limit)
                .items
            )
        elif order_by == ApplicationSortingParameters.Created:
            return (
                cls.query.order_by(Application.created.asc())
                .filter(Application.application_name.in_(form_names))
                .paginate(page_no, limit)
                .items
            )

        elif order_by == ApplicationSortingParameters.Name and sort_order == "asc":
            return (
                cls.query.order_by(Application.application_name.asc())
                .filter(Application.application_name.in_(form_names))
                .paginate(page_no, limit)
                .items
            )
        elif order_by == ApplicationSortingParameters.Name and sort_order == "desc":
            return (
                cls.query.order_by(Application.application_name.desc())
                .filter(Application.application_name.in_(form_names))
                .paginate(page_no, limit)
                .items
            )
        elif order_by == ApplicationSortingParameters.Status:
            return (
                cls.query.order_by(Application.application_status.asc())
                .filter(Application.application_name.in_(form_names))
                .paginate(page_no, limit)
                .items
            )
        elif order_by == ApplicationSortingParameters.Modified:
            return (
                cls.query.order_by(Application.modified.asc())
                .filter(Application.application_name.in_(form_names))
                .paginate(page_no, limit)
                .items
            )
        else:
            return (
                cls.query.filter(Application.application_name.in_(form_names))
                .order_by(Application.id.desc())
                .paginate(page_no, limit)
                .items
            )

    @classmethod
    def find_all_application_count(
        cls,
        form_names: str,
        application_id: int,
        created_from: str,
        created_to: str,
        modified_from: str,
        modified_to: str,
        application_name: str,
        application_status: str,
        created_by: str,
        order_by: str,
        sort_order: str,
    ):
        if application_id:
            return cls.query.filter(Application.id == application_id).filter(
                Application.application_name.in_(form_names)
            )
        elif application_name:
            return cls.query.filter(
                Application.application_name.like(f"{application_name}%")
            ).filter(Application.application_name.in_(form_names))
        elif application_status:
            return cls.query.filter(
                Application.application_status.like(f"{application_status}%")
            ).filter(Application.application_name.in_(form_names))
        elif created_by:
            return cls.query.filter(Application.created_by == created_by).filter(
                Application.application_name.in_(form_names)
            )
        elif created_from and created_to:
            return cls.query.filter(
                and_(
                    func.date(Application.created) >= created_from,
                    func.date(Application.created) <= created_to,
                )
            ).filter(Application.application_name.in_(form_names))
        elif modified_from and modified_to:
            return cls.query.filter(
                and_(
                    func.date(Application.modified) >= modified_from,
                    func.date(Application.modified) <= modified_to,
                )
            ).filter(Application.application_name.in_(form_names))
        """Fetch applications based on sorting parameters
        :qparam orderBy: Name of column to order by
        :qparam orderBy id: sorted applications based on id
        :qparam orderBy created: sorted applications based on date and time
        :qparam orderBy application_name: sorted applications based on application name
        :qparam orderBy application_status: sorted applications based on status
        :qparam orderBy modified: sorted applications based on modified date and time                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
        """
        if order_by == ApplicationSortingParameters.Id and sort_order == "asc":
            return cls.query.order_by(Application.id.asc()).filter(
                Application.application_name.in_(form_names)
            )
        elif order_by == ApplicationSortingParameters.Id and sort_order == "desc":
            return cls.query.order_by(Application.id.desc()).filter(
                Application.application_name.in_(form_names)
            )
        elif order_by == ApplicationSortingParameters.Created:
            return cls.query.order_by(Application.created.asc()).filter(
                Application.application_name.in_(form_names)
            )

        elif order_by == ApplicationSortingParameters.Name and sort_order == "asc":
            return cls.query.order_by(Application.application_name).filter(
                Application.application_name.in_(form_names)
            )
        elif order_by == ApplicationSortingParameters.Name and sort_order == "desc":

            return cls.query.order_by(Application.application_name).filter(
                Application.application_name.in_(form_names)
            )
        elif order_by == ApplicationSortingParameters.Status:
            return cls.query.order_by(Application.application_status.asc()).filter(
                Application.application_name.in_(form_names)
            )
        elif order_by == ApplicationSortingParameters.Modified:
            return cls.query.order_by(Application.modified.asc()).filter(
                Application.application_name.in_(form_names)
            )
        else:
            return cls.query.filter(
                Application.application_name.in_(form_names)
            ).order_by(Application.id.desc())

    @classmethod
    def find_all_applications_count(cls,
        user_id: str,
        application_id: int,
        created_from: str,
        created_to: str,
        modified_from: str,
        modified_to: str,
        application_name: str,
        application_status: str,
        created_by: str,
        order_by: str,
        sort_order: str,
    ):
        if application_id:
            return cls.query.filter(Application.id == application_id).filter(
                (Application.created_by == user_id)
            )
        elif application_name:
            return cls.query.filter(
                Application.application_name.like(f"{application_name}%")
            ).filter(Application.created_by == user_id)
        elif application_status:
            return cls.query.filter(
                Application.application_status.like(f"{application_status}%")
            ).filter(Application.created_by == user_id)
        elif created_by:
            return cls.query.filter(Application.created_by == created_by).filter(
                (Application.created_by == user_id)
            )
        elif created_from and created_to:
            return cls.query.filter(
                and_(
                    func.date(Application.created) >= created_from,
                    func.date(Application.created) <= created_to,
                )
            ).filter(Application.created_by == user_id)
        elif modified_from and modified_to:
            return cls.query.filter(
                and_(
                    func.date(Application.modified) >= modified_from,
                    func.date(Application.modified) <= modified_to,
                )
            ).filter(Application.created_by == user_id)
        """Fetch applications based on sorting parameters
        :qparam orderBy: Name of column to order by
        :qparam orderBy id: sorted applications based on id
        :qparam orderBy created: sorted applications based on date and time
        :qparam orderBy application_name: sorted applications based on application name
        :qparam orderBy application_status: sorted applications based on status
        :qparam orderBy modified: sorted applications based on modified date and time                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
        """
        if order_by == ApplicationSortingParameters.Id and sort_order == "asc":
            return cls.query.order_by(Application.id.asc()).filter(
                (Application.created_by == user_id)
            )
        elif order_by == ApplicationSortingParameters.Id and sort_order == "desc":
            return cls.query.order_by(Application.id.desc()).filter(
                (Application.created_by == user_id)
            )
        elif order_by == ApplicationSortingParameters.Created:
            return cls.query.order_by(Application.created.asc()).filter(
                (Application.created_by == user_id)
            )

        elif order_by == ApplicationSortingParameters.Name and sort_order == "asc":
            return cls.query.order_by(Application.application_name).filter(
                (Application.created_by == user_id)
            )
        elif order_by == ApplicationSortingParameters.Name and sort_order == "desc":

            return cls.query.order_by(Application.application_name).filter(
                (Application.created_by == user_id)
            )
        elif order_by == ApplicationSortingParameters.Status:
            return cls.query.order_by(Application.application_status.asc()).filter(
                (Application.created_by == user_id)
            )
        elif order_by == ApplicationSortingParameters.Modified:
            return cls.query.order_by(Application.modified.asc()).filter(
                (Application.created_by == user_id)
            )
        else:
            return cls.query.filter(
                (Application.created_by == user_id)
            ).order_by(Application.id.desc())
    @classmethod
    def find_all_applications(cls, page_no: int, limit: int, form_names: str):
        if page_no == 0:
            return cls.query.filter(
                Application.application_name.in_(form_names)
            ).order_by(Application.id.desc())
        else:
            return (
                cls.query.filter(Application.application_name.in_(form_names))
                .order_by(Application.id.desc())
                .paginate(page_no, limit, False)
                .items
            )

    @classmethod
    def find_id_by_form_names(cls, application_id: int, form_names):
        return cls.query.filter(
            and_(
                Application.application_name.in_(form_names),
                Application.id == application_id,
            )
        ).one_or_none()

    @classmethod
    def find_by_form_id_user(cls, form_id, user_id: str, page_no: int, limit: int):
        if page_no == 0:
            return (
                cls.query.filter(Application.form_url.like("%" + form_id + "%"))
                .filter(Application.created_by == user_id)
                .order_by(Application.id.desc())
            )
        else:
            return (
                cls.query.filter(Application.form_url.like("%" + form_id + "%"))
                .filter(Application.created_by == user_id)
                .order_by(Application.id.desc())
                .paginate(page_no, limit, False)
                .items
            )

    @classmethod
    def find_by_form_ids(cls, form_ids, page_no: int, limit: int):
        """Fetch application based on multiple form ids."""
        if page_no == 0:
            return cls.query.filter(
                or_(
                    Application.form_url.like("%" + form_id + "%")
                    for form_id in form_ids
                )
            ).order_by(Application.id.desc())
        else:
            return (
                cls.query.filter(
                    or_(
                        Application.form_url.like("%" + form_id + "%")
                        for form_id in form_ids
                    )
                )
                .order_by(Application.id.desc())
                .paginate(page_no, limit, False)
                .items
            )

    @classmethod
    def find_all_by_form_id_count(cls, form_id):
        """Fetch all application."""
        return cls.query.filter(Application.form_url.like("%" + form_id + "%")).count()

    @classmethod
    def find_all_by_form_id_user_count(cls, form_id, user_id: str):
        """Fetch all application."""
        return (
            cls.query.filter(Application.form_url.like("%" + form_id + "%"))
            .filter(Application.created_by == user_id)
            .count()
        )

    @classmethod
    def find_aggregated_applications(cls, from_date: str, to_date: str):
        """Fetch aggregated applications."""
        result_proxy = (
            db.session.query(
                Application.form_process_mapper_id,
                FormProcessMapper.form_name,
                func.count(Application.form_process_mapper_id).label("count"),
            )
            .join(
                FormProcessMapper,
                FormProcessMapper.id == Application.form_process_mapper_id,
            )
            .filter(
                func.date(Application.created) >= from_date,
                func.date(Application.created) <= to_date,
            )
            .group_by(Application.form_process_mapper_id, FormProcessMapper.form_name)
        )

        result = []
        for row in result_proxy:
            info = dict(row)
            result.append(info)

        return result

    @classmethod
    def find_aggregated_applications_modified(cls, from_date: str, to_date: str):
        """Fetch aggregated applications."""
        result_proxy = (
            db.session.query(
                Application.form_process_mapper_id,
                FormProcessMapper.form_name,
                func.count(Application.form_process_mapper_id).label("count"),
            )
            .join(
                FormProcessMapper,
                FormProcessMapper.id == Application.form_process_mapper_id,
            )
            .filter(
                func.date(Application.modified) >= from_date,
                func.date(Application.modified) <= to_date,
            )
            .group_by(Application.form_process_mapper_id, FormProcessMapper.form_name)
        )

        result = []
        for row in result_proxy:
            info = dict(row)
            result.append(info)

        return result

    @classmethod
    def find_aggregated_application_status(
        cls, mapper_id: int, from_date: str, to_date: str
    ):
        """Fetch aggregated application status."""
        result_proxy = (
            db.session.query(
                Application.application_status,
                Application.application_name,
                func.count(Application.application_name).label("count"),
            )
            .join(
                FormProcessMapper,
                FormProcessMapper.id == Application.form_process_mapper_id,
            )
            .filter(
                and_(
                    func.date(Application.created) >= from_date,
                    func.date(Application.created) <= to_date,
                    Application.form_process_mapper_id == mapper_id,
                )
            )
            .group_by(Application.application_status, Application.application_name)
        )

        return result_proxy

    @classmethod
    def find_aggregated_application_status_modified(
        cls, mapper_id: int, from_date: str, to_date: str
    ):
        """Fetch aggregated application status."""
        result_proxy = (
            db.session.query(
                Application.application_name,
                Application.application_status,
                func.count(Application.application_name).label("count"),
            )
            .filter(
                and_(
                    func.date(Application.modified) >= from_date,
                    func.date(Application.modified) <= to_date,
                    Application.form_process_mapper_id == mapper_id,
                )
            )
            .group_by(Application.application_name, Application.application_status)
        )

        return result_proxy
