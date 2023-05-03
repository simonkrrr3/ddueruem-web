import {ConfigurationCommand} from "@/classes/Commands/Configurator/ConfigurationCommand";
import {SelectionState} from "@/classes/Configurator/SelectionState";
import api from "@/services/api.service";

export class SelectionCommand extends ConfigurationCommand {
    constructor(featureModel, featureOrVersion, newSelectionState) {
        super(featureModel);
        this.featureOrVersion = featureOrVersion;
        this.newSelectionState = newSelectionState;
        this.executed = false;
        this.newSatCount = 0;
    }
    execute() {
        if (!this.executed) {
            if (this.featureOrVersion.selectionState === this.newSelectionState) {
                this.featureOrVersion.selectionState = SelectionState.Unselected;
            } else {
                this.featureOrVersion.selectionState = this.newSelectionState;
            }

            const selected_roots = this.featureModel.versions.filter(v => v.selectionState === SelectionState.ExplicitlySelected).map(v => v.id);
            const available_roots = this.featureModel.versions.filter(v => !selected_roots.includes(v) && v.selectionState !== SelectionState.ExplicitlyDeselected).map(v => v.id)
            const selected_vars = this.featureModel.features.filter(f => f.selectionState === SelectionState.ExplicitlySelected).map(f => f.id);
            const deselected_vars = this.featureModel.features.filter(f => f.selectionState === SelectionState.ExplicitlyDeselected).map(f => -f.id);
            const config = [...selected_vars, ...deselected_vars];

            api.post(`${process.env.VUE_APP_DOMAIN}configurator/`, ({"config": config, "selected_roots": selected_roots, "available_roots": available_roots}))
                .then((d) => {
                    const data = d.data;
                    this.newSatCount = data.count;

                    this.newExplicitlySelectedVersions = this.featureModel.versions.filter(v => data.selected_roots.includes(v.id) && v.selectionState === SelectionState.ExplicitlySelected)
                    this.newImplicitlySelectedVersions = this.featureModel.versions.filter(v => data.selected_roots.includes(v.id) && v.selectionState !== SelectionState.ExplicitlySelected)
                    this.newExplicitlyDeselectedVersions = this.featureModel.versions.filter(v => v.selectionState === SelectionState.ExplicitlyDeselected)
                    this.newImplicitlyDeselectedVersions = this.featureModel.versions.filter(v => data.deselected_roots.includes(v.id) && v.selectionState !== SelectionState.ExplicitlyDeselected)
                    this.newUnselectedVersions = this.featureModel.versions.filter(v => data.available_roots.includes(v.id) && v.selectionState !== SelectionState.ExplicitlyDeselected)

                    this.newExplicitlySelectedFeatures = this.featureModel.features.filter(f => data.config.includes(f.id))
                    this.newImplicitlySelectedFeatures = this.featureModel.features.filter(f => data.implicit_selected_vars.includes(f.id))
                    this.newExplicitlyDeselectedFeatures = this.featureModel.features.filter(f => data.config.includes(-f.id))
                    this.newImplicitlyDeselectedFeatures = this.featureModel.features.filter(f => data.implicit_deselected_vars.includes(f.id))
                    this.newUnselectedFeatures = this.featureModel.features.filter(f => data.available_vars.includes(f.id))

                    this.executed = true;

                    super.execute();
                })
                .catch(() => {
                    this.addLoading = false;
                });

        } else {
            super.execute();
        }
    }
}