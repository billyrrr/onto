"""

Contains test cases inspired by flasgger (MIT licence)
See: https://github.com/flasgger/flasgger/blob/master/LICENSE
"""
import time

from flask import Flask, jsonify
from flasgger import Swagger, SwaggerView
from google.cloud.firestore import DocumentReference

from onto.view import GenericView
from onto import fields
from onto.schema import Schema
from onto.view_model import ViewModel
from onto.domain_model import DomainModel
from google.cloud import firestore
from onto import testing_utils
from functools import partial

from examples.luggage_models import LuggageItem, Luggages

from onto.config import Config
from onto.context import Context as CTX

if __name__ == "__main__":
    config = Config(
        app_name="flask-boiler-testing",
        debug=True,
        testing=True,
        certificate_filename="flask-boiler-testing-firebase-adminsdk-4m0ec-7505aaef8d.json"
    )

    CTX.read(config)

    d_a = {
            "luggage_type": "large",
            "weight_in_lbs": 20,
            "obj_type": "LuggageItem"
        }
    id_a = "luggage_id_a"
    obj_a = LuggageItem.new(id_a)
    obj_a._import_properties(d_a)
    obj_a.save()

    d_b = {
            "luggage_type": "medium",
            "weight_in_lbs": 15,
            "obj_type": "LuggageItem"
        }
    id_b = "luggage_id_b"
    obj_b = LuggageItem.new(id_b)
    obj_b._import_properties(d_b)
    obj_b.save()

    vm_ref: DocumentReference = CTX.db.document("test_lugagges/user_a_luggages")

    vm: Luggages = Luggages.new(vm_ref)

    vm.bind_to(key=id_a, obj_type="LuggageItem", doc_id=id_a)
    vm.bind_to(key=id_b, obj_type="LuggageItem", doc_id=id_b)
    vm.register_listener()

    # Takes time to propagate changes
    testing_utils._wait(factor=.5)

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

    testing_utils._wait(factor=.3)

    # # Test that the view model now has updated values
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
