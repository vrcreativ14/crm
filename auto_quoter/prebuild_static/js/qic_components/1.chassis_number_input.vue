<template>
    <div>
        <div class="form-group">
            <label for="chassis-number" class="label">Chassis Number</label>
            <input type="text" id="chassis-number" name="chassis-number" class="form-control" v-model="chassisNumber"
                   :disabled="isLoading">
        </div>
        <button type="button" class="btn btn-secondary" :disabled="!canLoadCarInfo()" @click="loadCarInfo">Load Car
            Information
        </button>
        <div v-if="isLoading">
            Loading car info...
        </div>
        <div v-if="hasError">
            {{ errorMessage }}
        </div>
    </div>
</template>

<script>
export default {
    name: "chassis-number-input",
    props: ["initialChassisNumber"],
    data: function () {
        return {
            chassisNumber: this.initialChassisNumber,
            isLoading: false,
            hasError: false,
            errorMessage: ""
        }
    },
    methods: {
        canLoadCarInfo() {
            return !this.isLoading && this.chassisNumber.length > 0;
        },
        loadCarInfo() {
            this.isLoading = true;
            this.hasError = false;

            $.get(qicVehicleInfoUrl, {chassisNumber: this.chassisNumber})
                    .done((response) => {
                        const vehicleInfo = {
                            "chassisNumber": this.chassisNumber,
                            "makeCode": response["makeCode"],
                            "modelCode": response["modelCode"],
                            "yearCode": response["yearCode"]
                        };
                        this.$emit("car-info-loaded", vehicleInfo);
                    })
                    .fail((xhr) => {
                        this.hasError = true;
                        this.errorMessage = xhr.responseText;
                    })
                    .always(() => {
                        this.isLoading = false;
                    });
        }
    }
}
</script>

<style scoped>

</style>