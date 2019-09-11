"""

Contains test cases inspired by flasgger (MIT licence)
See: https://github.com/flasgger/flasgger/blob/master/LICENSE
"""
import time

from flask import Flask, jsonify
from flasgger import Swagger, SwaggerView
from google.cloud.firestore import DocumentReference

from flask_boiler.view import GenericView
from flask_boiler import fields
from flask_boiler.schema import Schema
from flask_boiler.view_model import ViewModel
from flask_boiler.domain_model import DomainModel
from google.cloud import firestore
from functools import partial

from examples.luggage_models import LuggageItem, Luggages

from flask_boiler.config import Config
from flask_boiler.context import Context as CTX

if __name__ == "__main__":
    config = Config(
        app_name="gravitate-dive-testing",
        debug=True,
        testing=True,
        certificate_filename="gravitate-dive-testing-firebase-adminsdk-g1ybn-2dde9daeb0.json"
    )

    CTX.read(config)

    d_a = {
            "luggage_type": "large",
            "weight_in_lbs": 20,
            "obj_type": "LuggageItem"
        }
    id_a = "luggage_id_a"
    obj_a = LuggageItem.create(id_a)
    obj_a._import_properties(d_a)
    obj_a.save()

    d_b = {
            "luggage_type": "medium",
            "weight_in_lbs": 15,
            "obj_type": "LuggageItem"
        }
    id_b = "luggage_id_b"
    obj_b = LuggageItem.create(id_b)
    obj_b._import_properties(d_b)
    obj_b.save()

    vm_ref: DocumentReference = CTX.db.document("test_lugagges/user_a_luggages")

    vm: Luggages = Luggages.create(vm_ref)

    vm.bind_to(key=id_a, obj_type="LuggageItem", doc_id=id_a)
    vm.bind_to(key=id_b, obj_type="LuggageItem", doc_id=id_b)

    # Takes time to propagate changes
    time.sleep(2)

    # assert vm_ref.get().to_dict() == {
    #         "luggages": [
    #             {
    #                 "luggage_type": "large",
    #                 "weight_in_lbs": 20
    #             },
    #             {
    #                 "luggage_type": "medium",
    #                 "weight_in_lbs": 15
    #             }
    #         ],
    #         "total_weight": 35,
    #         "total_count": 2,
    #         # "obj_type": "Luggages"
    #     }
    assert vm.to_dict() == {
        "luggages": [
            {
                "luggage_type": "large",
                "weight_in_lbs": 20
            },
            {
                "luggage_type": "medium",
                "weight_in_lbs": 15
            }
        ],
        "total_weight": 35,
        "total_count": 2,
        # "obj_type": "Luggages"
    }

    # Change the weight on one of the luggages
    obj_b.weight_in_lbs = 25
    obj_b.save()

    # Note that the update is eventually consistent with delays
    #   and local copies of a ViewModel should not be used to read
    #   updated values

    time.sleep(2)

    # # Test that the view model now has updated values
    # assert vm_ref.get().to_dict() == {
    #         "luggages": [
    #             {
    #                 "luggage_type": "large",
    #                 "weight_in_lbs": 20
    #             },
    #             {
    #                 "luggage_type": "medium",
    #                 "weight_in_lbs": 25
    #             }
    #         ],
    #         "total_weight": 45,
    #         "total_count": 2
    #     }

    assert vm.to_dict() == {
        "luggages": [
            {
                "luggage_type": "large",
                "weight_in_lbs": 20
            },
            {
                "luggage_type": "medium",
                "weight_in_lbs": 25
            }
        ],
        "total_weight": 45,
        "total_count": 2
    }
