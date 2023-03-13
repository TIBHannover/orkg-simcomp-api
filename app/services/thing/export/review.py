# -*- coding: utf-8 -*-
import http
from typing import Any, Dict, Union
from xml.sax.saxutils import escape

import pandas as pd
from pydantic import ValidationError

from app.common.errors import OrkgSimCompApiError
from app.models.review import Review
from app.models.thing import ExportFormat, ThingType


class ReviewExporter:
    @staticmethod
    def export(
        review: Union[dict, Review],
        format: ExportFormat,
        config: Dict[str, Any] = None,
        thing_service: ... = None,
        **kwargs,
    ):
        review = ReviewExporter._parse(review)

        try:
            return {
                format.XML: ReviewExporter._export_xml,
            }[
                format
            ](review, config, thing_service)
        except KeyError:
            raise OrkgSimCompApiError(
                message='Exporting a review with the format="{}" is not supported'.format(format),
                cls=ReviewExporter,
                status_code=http.HTTPStatus.NOT_IMPLEMENTED,
            )

    @staticmethod
    def _export_xml(review: Review, config: Dict[str, Any], thing_service):
        # reading the fields from the Review object
        review_classes = next(
            (
                statement.subject.classes
                for statement in review.statements
                if statement.subject.id == review.root_review_id
            ),
            None,
        )

        if "SmartReview" not in review_classes:
            raise OrkgSimCompApiError(
                message="Review is not of class SmartReview",
                cls=ReviewExporter,
                status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,  # TODO: or bad request as we had ?
            )

        # prepare article metadata
        title = next(
            (
                statement.subject.label
                for statement in review.statements
                if statement.subject.id == review.root_review_id
            ),
            None,
        )

        review_contribution = next(
            (
                statement.object.id
                for statement in review.statements
                if statement.predicate.id == "P31"
                and statement.subject.id == review.root_review_id
            ),
            None,
        )

        field = next(
            (
                statement.object.label
                for statement in review.statements
                if statement.predicate.id == "P30"
                and statement.subject.id == review.root_review_id
            ),
            None,
        )

        publication_date = next(
            (
                statement.subject.created_at
                for statement in review.statements
                if statement.subject.id == review.root_review_id
            ),
            None,
        )
        day, month, year = publication_date.day, publication_date.month, publication_date.year

        authors = [
            statement.object.label
            for statement in review.statements
            if statement.predicate.id == "P27" and statement.subject.id == review.root_review_id
        ]

        section_ids = [
            statement.object.id
            for statement in review.statements
            if statement.predicate.id == "HasSection"
            and statement.subject.id == review_contribution
        ]

        sections_jats = ""

        # Start creating the xml
        authors_jats = "".join(
            [ReviewExporter._generate_template_author(author) for author in authors]
        )

        for section_id in reversed(section_ids):
            section = next(
                (
                    statement.object
                    for statement in review.statements
                    if statement.object.id == section_id
                ),
                None,
            )
            section_type = " ".join(section.classes).replace("Section", "").strip().lower()
            section_content = ""

            # for text/content sections in Markdown
            if "Section" in section.classes:
                section_content = escape(
                    next(
                        (
                            statement.object.label
                            for statement in review.statements
                            if statement.subject.id == section_id
                            and statement.predicate.id == "hasContent"
                        ),
                        None,
                    )
                )

            # comparison section
            if "ComparisonSection" in section.classes:
                comparison = next(
                    (
                        statement.object
                        for statement in review.statements
                        if statement.subject.id == section_id
                        and statement.predicate.id == "HasLink"
                    ),
                    None,
                )

                if not comparison:
                    continue

                comparison_id = comparison.id
                comparison_description = next(
                    (
                        statement.object.label
                        for statement in review.statements
                        if statement.subject.id == comparison_id
                        and statement.predicate.id == "description"
                    ),
                    None,
                )

                try:
                    comparison_table = thing_service.export_thing(
                        ThingType.COMPARISON, comparison_id, format=ExportFormat.HTML, like_ui=True
                    )
                except OrkgSimCompApiError:
                    comparison_table = pd.DataFrame().to_html()

                section_content = ReviewExporter._generate_template_section_comparison(
                    comparison_title=comparison.label,
                    comparison_description=comparison_description,
                    comparison_table=comparison_table,
                )

            # visualization section
            if "VisualizationSection" in section.classes:
                visualization_id = next(
                    (
                        statement.object.id
                        for statement in review.statements
                        if statement.subject.id == section_id
                        and statement.predicate.id == "HasLink"
                    ),
                    None,
                )

                if not visualization_id:
                    continue

                section_content = (
                    f'Visualization can be viewed via <a href="https://orkg.org/resource/{visualization_id}">'
                    f"the ORKG website</a>."
                )

            # property and resource sections
            if "PropertySection" in section.classes or "ResourceSection" in section.classes:
                section_entity_id = next(
                    (
                        statement.object.id
                        for statement in review.statements
                        if statement.subject.id == section_id
                        and statement.predicate.id == "HasLink"
                    ),
                    None,
                )

                if not section_entity_id:
                    continue

                entity_statements = [
                    statement
                    for statement in review.statements
                    if statement.subject.id == section_entity_id
                ]

                rows = ""
                for statement in entity_statements:
                    rows += ReviewExporter._generate_template_entity_table_row(
                        predicate_label=statement.predicate.label,
                        object_label=statement.object.label,
                    )

                section_content = ReviewExporter._generate_template_entity_table(rows=rows)

            section_jats = ReviewExporter._generate_template_section(
                section_type=section_type,
                section_title=section.label,
                section_content=section_content,
            )
            sections_jats += section_jats

        jats = ReviewExporter._generate_template_article(
            field=field,
            title=title,
            authors=authors_jats,
            publication_day=day,
            publication_month=month,
            publication_year=year,
            sections=sections_jats,
        )

        return jats

    @staticmethod
    def _parse(review: Union[dict, Review]) -> Review:
        if isinstance(review, Review):
            return review

        try:
            return Review(root_review_id=review["root_review_id"], statements=review["statements"])
        except (KeyError, ValidationError):
            raise OrkgSimCompApiError(
                message="Data object cannot be parsed as a Review",
                cls=ReviewExporter,
                status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
            )

    @staticmethod
    def _generate_template_author(author):
        return f"""<contrib contrib-type="person">
                <string-name>{author}</string-name>
            </contrib>
        """

    @staticmethod
    def _generate_template_section_comparison(
        comparison_title, comparison_description, comparison_table
    ):
        return f"""<table-wrap>
                <label>{comparison_title}</label>
                <caption>
                    <title>{comparison_description}</title>
                </caption>
                {comparison_table}
            </table-wrap>
        """

    @staticmethod
    def _generate_template_entity_table_row(predicate_label, object_label):
        return f"""<tr>
                <td>{predicate_label}</td>
                <td>{object_label}</td>
            </tr>
        """

    @staticmethod
    def _generate_template_entity_table(rows):
        return f"""<table-wrap>
                <label>sdf</label>
                <caption>
                    <title>asdf</title>
                </caption>
                <table>
                    <thead>
                        <tr>
                            <th>Property</th>
                            <th>Value</th>
                        </tr>
                    </thead>
                    <tbody>{rows}</tbody>
                </table>
            </table-wrap>
        """

    @staticmethod
    def _generate_template_section(section_type, section_title, section_content):
        return f"""<sec sec-type="{section_type}">
                <title>{section_title}</title>
                <p>{section_content}</p>
            </sec>
        """

    @staticmethod
    def _generate_template_article(
        field, title, authors, publication_day, publication_month, publication_year, sections
    ):
        return f"""<?xml version="1.0" encoding="UTF-8"?>
            <article xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:ali="http://www.niso.org/schemas/ali/1.0">
                <front>
                    <article-meta>
                        <article-categories>
                            <subj-group xml:lang="en">
                                <subject>{field}</subject>
                            </subj-group>
                        </article-categories>
                        <title-group>
                            <article-title>{title}</article-title>
                        </title-group>
                        <contrib-group content-type="author">{authors}</contrib-group>
                        <pub-date date-type="pub" iso-8601-date="
                            {publication_year}-{publication_month}-{publication_day}">
                            <day>{publication_day}</day>
                            <month>{publication_month}</month>
                            <year>{publication_year}</year>
                        </pub-date>
                        <permissions id="permission">
                            <copyright-year>{publication_year}</copyright-year>
                            <copyright-holder>Open Research Knowledge Graph</copyright-holder>
                            <license>
                                <ali:license_ref>http://creativecommons.org/licenses/by-sa/4.0/</ali:license_ref>
                                <license-p>This work is licensed under a Creative Commons Attribution-ShareAlike 4.0
                                 International License (CC BY-SA 4.0)</license-p>
                            </license>
                        </permissions>
                    </article-meta>
                </front>
                <body id="body">
                    {sections}
                </body>
            </article>
        """
