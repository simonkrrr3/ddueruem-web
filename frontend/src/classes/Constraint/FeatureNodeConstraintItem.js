import {ConstraintItem} from "@/classes/Constraint/ConstraintItem";

export class FeatureNodeConstraintItem extends ConstraintItem {
    constructor(featureNode) {
        super();
        this.featureNode = featureNode;
    }

    count() {
        return 1;
    }

    toString() {
        return this.featureNode.name;
    }

    toStringForEdit() {
        return this.toString();
    }

    toStringPostfix() {
        return this.toString();
    }

    toStringXML() {
        return `<var>${this.featureNode.name}</var>`;
    }

    getFeatureNodes() {
        return [this.featureNode];
    }

    setConstraint(constraint) {
        this.constraint = constraint;
        if (!this.featureNode.constraints.includes(this.constraint))
            this.featureNode.constraints.push(this.constraint);
    }
}
