# dune_query_service.py

from dataclasses import dataclass
from datetime import datetime
from typing import Annotated, Literal
from dune_client.client import DuneClient
from dune_client.query import QueryBase
from dune_client.types import QueryParameter
from pydantic import Field

from config import API_KEY, REQUEST_TIMEOUT


class AdditionalParam:
    param_type: str


@dataclass
class StrParam(AdditionalParam):
    name: str
    value: str
    param_type: Literal["text"] = "text"

    def to_query_param(self) -> QueryParameter:
        return QueryParameter.text_type(name=self.name, value=self.value)


@dataclass
class NumParam(AdditionalParam):
    name: str
    value: int | float
    param_type: Literal["number"] = "number"

    def to_query_param(self) -> QueryParameter:
        return QueryParameter.number_type(name=self.name, value=self.value)


@dataclass
class DateParam(AdditionalParam):
    name: str
    value: datetime | str
    param_type: Literal["date"] = "date"

    def to_query_param(self) -> QueryParameter:
        return QueryParameter.date_type(name=self.name, value=self.value)


@dataclass
class EnumParam(AdditionalParam):
    name: str
    value: str
    param_type: Literal["enum"] = "enum"

    def to_query_param(self) -> QueryParameter:
        return QueryParameter.enum_type(name=self.name, value=self.value)


DuneParam = Annotated[
    StrParam | NumParam | DateParam | EnumParam, Field(discriminator="param_type")
]


class DuneParamFactory:

    @staticmethod
    def from_param_type(
        name: str, value: str, param_type: Literal["text", "number", "date", "enum"]
    ) -> AdditionalParam:

        if param_type == "text":
            return StrParam(name=name, value=value, param_type=param_type)
        if param_type == "number":
            return NumParam(name=name, value=value, param_type=param_type)
        if param_type == "date":
            return DateParam(name=name, value=value, param_type=param_type)
        if param_type == "enum":
            return EnumParam(name=name, value=value, param_type=param_type)
        raise ValueError(f"Unknown param_type: {param_type}")


@dataclass
class DuneQueryParams:
    query_id: int
    query_name: str
    additional_params: list[DuneParam] | None = None


@dataclass
class DuneQueryConfigs:
    params: list[DuneQueryParams]

    def add_param(self, param: DuneQueryParams) -> None:
        self.params.append(param)


class DuneQueryService:
    def __init__(self, config: DuneQueryConfigs):
        self.config = config
        self.client = DuneClient(
            api_key=API_KEY,
            base_url="https://api.dune.com",
            request_timeout=REQUEST_TIMEOUT,
        )

    def _build_parameters(
        self, additional_params: list[DuneParam] | None
    ) -> list[QueryParameter]:
        if not additional_params:
            return []
        return [param.to_query_param() for param in additional_params]

    def get_query_params_by_name(self, query_name: str) -> DuneQueryParams:
        query_params = next(
            (q for q in self.config.params if q.query_name == query_name), None
        )
        if query_params is None:
            msg = f"Query with name {query_name} not found in configuration"
            raise ValueError(msg)

        return query_params

    def fetch_and_export_query(
        self, query_name: str, export_path: str | None = None
    ) -> None:
        query_config = self.get_query_params_by_name(query_name)
        query = QueryBase(
            name=query_config.query_name,
            query_id=query_config.query_id,
            params=self._build_parameters(query_config.additional_params),
        )
        df = self.client.run_query_dataframe(query)
        export_file = export_path or f"{query_name}.csv"
        df.to_csv(export_file, index=False)


if __name__ == "__main__":
    config = DuneQueryConfigs(
        params=[
            DuneQueryParams(
                query_id=4732812,
                query_name="dune_query_fees",
                additional_params=[
                    DuneParamFactory.from_param_type(
                        name="pool_address",
                        value="0xebd5311bea1948e1441333976eadcfe5fbda777c",
                        param_type="text",
                    )
                ],
            ),
            DuneQueryParams(query_id=4842271, query_name="mint_burn"),
        ]
    )

    dune_service = DuneQueryService(config)
    dune_service.fetch_and_export_query("mint_burn")
