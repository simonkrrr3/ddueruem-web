from rest_framework.views import APIView
from rest_framework.response import Response
import os
import re

from .libdddmp import parse_from_ddueruem
from .serializers import ConfigurationRequestSerializer, DecisionPropagationSerializer, ExplanationsSerializer


class DecisionPropagation(APIView):
    bdds = {}

    def get(self, request):
        paras = [{"config": [1,2,3,4,5], "selected_roots": [1,2]}]
        serializer = ConfigurationRequestSerializer(paras, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ConfigurationRequestSerializer(data=request.data)
        if serializer.is_valid():
            name = request.data['name']
            config = request.data['config']
            selected_roots = request.data['selected_roots']
            available_roots = request.data['available_roots']
            if len(available_roots) == 0:
                available_roots = None

            bdd = init(name)

            count, available_vars, simpl_vars, dimpl_vars = bdd.decision_propagation_multiversion_features(config, selected_roots, available_roots)
            available_roots, deselected_roots = bdd.decision_propagation_multiversion_versions(config, selected_roots, available_roots)

            results = {"config": config, "selected_roots": selected_roots, "count": count,
                     "available_vars": available_vars,
                     "implicit_selected_vars": simpl_vars, "implicit_deselected_vars": dimpl_vars,
                     "available_roots": available_roots, "deselected_roots": deselected_roots}

            serializer = DecisionPropagationSerializer(results)

            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

def init(name):
    if name in DecisionPropagation.bdds:
        return DecisionPropagation.bdds[name]
    else:
        bdd = parse_from_ddueruem("data/" + name + "/" + name + ".bdd")
        bdd.nodes_per_root = dict(
            [(root, set([var for _, var, high, low in bdd.get_nodes(root)])) for root in bdd.roots])
        DecisionPropagation.bdds[name] = bdd
        return bdd


class FeatureModels(APIView):
    def get(self, request, name, version_name):
        feature_model_path = "data/" + name + "/feature-models/" + version_name + ".xml"

        if not os.path.isfile(feature_model_path):
            return Response(status=404)

        with open(feature_model_path) as file:
            return Response(file.read(), status=200)


class Mappings(APIView):
    def get(self, request, name):
        root_mapping_file_path = "data/" + name + "/" + name + ".bdd-mapping"
        feature_mapping_dir = "data/" + name + "/dimacs"

        if not os.path.isfile(root_mapping_file_path):
            return Response(status=404)

        root_mapping = []
        with open(root_mapping_file_path) as root_mapping_file:
            for i, line in enumerate(root_mapping_file):
                if m := re.match(r"(?P<version_name>\S*)-SNG.dimacs-(?P<root_index>\d+)-(?P<number_of_roots>\d+):(?P<root_id>\d+)", line):
                    root_mapping.append({"version-name": m['version_name'], "root-id": int(m['root_id'])})

        feature_mapping = []
        with open(feature_mapping_dir + "/" + os.listdir(feature_mapping_dir)[0]) as feature_mapping_file:
            for line in feature_mapping_file:
                if m := re.match(r"c\s(?P<var_id>\d+)\s(?P<var_name>.+)", line):
                    feature_mapping.append({"var-name": m["var_name"], "var-id": int(m["var_id"])})


        result = {"root-mapping": root_mapping, "feature-mapping": feature_mapping}
        return Response(result, status=200)


class Explanations(APIView):
    def post(self, request, name):
        serializer = ExplanationsSerializer(data=request.data)
        if serializer.is_valid():
            vars = request.data['vars']
            config = request.data['config']
            selected_roots = request.data['selected_roots']

            bdd = init(name)

            #explanations = bdd.explanations_feature(var, config, selected_roots)
            selected_roots = set(selected_roots)

            conflicting_versions = set()
            available_versions = set()
            if len(selected_roots) == 0:
                available_versions = set(bdd.roots)
            else:
                # Step 1: Test if versions are valid
                if not bdd.verify_multiversion(vars, selected_roots):

                    # Step 2: Find all conflicting single versions
                    available_versions, conflicting_versions = bdd.decision_propagation_multiversion_versions(vars, [], selected_roots)

                    roots = []
                    for root in available_versions:
                        if bdd.verify_multiversion(vars, [root] + roots):
                            roots = roots + [root]
                    conflicting_versions = conflicting_versions.union(selected_roots.difference(roots))
                    selected_roots = selected_roots.difference(conflicting_versions)

            pc = vars
            if len(selected_roots) == 0:
                roots = set(bdd.roots)
                for c in config:
                    invalid_roots = set()
                    for root in roots:
                    #count, _, _, _, _ = bdd.decision_propagation2([c] + pc, roots)
                        if bdd.verify_multiversion([c] + pc, [root]):
                            #if count != 0:
                            pc = pc + [c]
                            roots = roots.difference(invalid_roots)
                            break
                        else:
                            invalid_roots.add(root)
            else:
                for c in config:
                    if bdd.verify_multiversion([c] + pc, selected_roots):
                        pc = pc + [c]

            available_roots, deselected_roots = bdd.decision_propagation_multiversion_versions(config, list(selected_roots), set(bdd.roots).difference(conflicting_versions))
            count, available_vars, simpl_vars, dimpl_vars = bdd.decision_propagation_multiversion_features(pc, selected_roots, set(bdd.roots).difference(conflicting_versions))

            results = {"config": pc, "selected_roots": selected_roots, "count": count,
                       "available_vars": available_vars,
                       "implicit_selected_vars": simpl_vars, "implicit_deselected_vars": dimpl_vars,
                       "available_roots": available_roots, "deselected_roots": deselected_roots.union(conflicting_versions)}

            serializer = DecisionPropagationSerializer(results)

            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)



