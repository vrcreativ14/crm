<template>
    <div>
        <div v-if="state === 'loading-vehicle-data'">
            Loading vehicle data...
        </div>
        <div v-if="state === 'error'" class="text-danger">
            {{ errorMessage }}
        </div>
        <template v-if="state === 'can-get-quotes'">
            <div class="form-group row">
                <label for="insured-name" class="col-form-label col-4">Name of insured</label>
                <div class="col-8">
                    <input type="text" class="form-control" id="insured-name" v-model="insuredName" required>
                </div>
            </div>
            <div class="form-group row">
                <label for="dob" class="col-form-label col-4">Date of birth</label>
                <div class="col-8">
                    <input type="date" class="form-control" id="dob" v-model="dob" required>
                </div>
            </div>
            <div class="form-group row">
                <label for="nationality" class="col-form-label col-4">Nationality</label>
                <div class="col-8">
                    <select id="nationality" class="custom-select" v-model="nationality" required>
                        <option v-for="country in countryList" :value="country[0]">{{ country[1] }}</option>
                    </select>
                </div>
            </div>
            <div class="form-group row">
                <label for="gulf-driving-experience" class="col-form-label col-8">Years of Gulf driving
                    experience</label>
                <div class="col-4">
                    <select id="gulf-driving-experience" class="custom-select" v-model="gulfDrivingExperience" required>
                        <option value="0">0 years</option>
                        <option value="1">1 year</option>
                        <option value="2">2 years</option>
                        <option value="3">3 years</option>
                        <option value="4">4 years</option>
                        <option value="5">5 years</option>
                        <option value="6">6 years</option>
                        <option value="7">7 years</option>
                        <option value="8">8 years</option>
                        <option value="9">9 years</option>
                        <option value="10">10+ years</option>
                    </select>
                </div>
            </div>

            <div class="form-group row">
                <label for="sum-insured" class="col-form-label col-4">Sum Insured</label>
                <div class="col-8">
                    <input type="number" step="1" class="form-control" id="sum-insured" v-model="sumInsured" required>
                </div>
            </div>
            <div class="form-group row">
                <label for="vehicle-usage" class="col-form-label col-4">Vehicle Usage</label>
                <div class="col-8">
                    <select id="vehicle-usage" class="custom-select" v-model="vehicleUsage" required>
                        <option value="1001">Private</option>
                        <option value="1002">Commercial</option>
                    </select>
                </div>
            </div>
            <div class="form-group row">
                <label class="col-form-label col-6" for=first-registration-date>Date of first registration</label>
                <div class="col-6 pt-2">
                    <input type="date" id="first-registration-date" class="form-control"
                           v-model="firstRegistrationDate">
                </div>
            </div>
            <div class="form-group row">
                <label class="col-form-label col-7" for=previous-insurance-valid>Is previous insurance still
                    active?</label>
                <div class="col-5 pt-2">
                    <input type="checkbox" id="previous-insurance-valid" v-model="previousInsuranceValid">
                </div>
            </div>
            <div class="form-group row">
                <label class="col-form-label col-6" for=total-loss-vehicle>Is this a total loss vehicle?</label>
                <div class="col-6 pt-2">
                    <input type="checkbox" id="total-loss-vehicle" v-model="totalLossVehicle">
                </div>
            </div>
            <div class="form-group row">
                <label for="no-claim-years" class="col-form-label col-8">Years with no claims (with certificate)</label>
                <div class="col-4">
                    <select id="no-claim-years" class="custom-select" v-model="noClaimYears" required>
                        <option value="0">0 years</option>
                        <option value="1">1 year</option>
                        <option value="2">2 years</option>
                        <option value="3">3 years</option>
                        <option value="4">4 years</option>
                        <option value="5">5 years</option>
                    </select>
                </div>
            </div>
            <div class="form-group row">
                <label for="no-claim-years-self-dec" class="col-form-label col-8">Years with no claims (self
                    declaration)</label>
                <div class="col-4">
                    <select id="no-claim-years-self-dec" class="custom-select" v-model="noClaimYearsSelfDec" required>
                        <option value="0">0 years</option>
                        <option value="1">1 year</option>
                        <option value="2">2 years</option>
                        <option value="3">3 years</option>
                        <option value="4">4 years</option>
                        <option value="5">5 years</option>
                    </select>
                </div>
            </div>
            <div class="row">
                <button class="btn btn-primary" @click="getQuotes">Get Quotes</button>
            </div>
        </template>
        <div v-if="state === 'getting-quotes'">
            Getting quotes...
        </div>
    </div>
</template>

<script>
export default {
    name: "get-quotes",
    props: ["vehicleInfo", "selectedTrim"],
    data() {
        return {
            state: "loading-vehicle-data",
            errorMessage: "",

            vehicleData: null,

            insuredName: window.qicAutoQuoterInitialData.name,
            dob: window.qicAutoQuoterInitialData.dob,
            nationality: window.qicAutoQuoterInitialData.nationality,

            countryList: qicCountryList,

            sumInsured: 0,
            vehicleUsage: "1001",

            firstRegistrationDate: window.qicAutoQuoterInitialData.firstRegistrationDate,

            previousInsuranceValid: true,
            totalLossVehicle: false,
            noClaimYears: window.qicAutoQuoterInitialData.noClaims,
            noClaimYearsSelfDec: window.qicAutoQuoterInitialData.noClaimsSelfDec,

            gulfDrivingExperience: window.qicAutoQuoterInitialData.gulfDrivingExperience,
        };
    },
    methods: {
        getRequestData() {
            return {
                name: this.insuredName,

                makeCode: this.vehicleData['makeCode'],
                modelCode: this.vehicleData['modelCode'],
                modelYear: this.vehicleData['modelYear'],

                sumInsured: this.sumInsured,
                vehicleType: this.vehicleData['bodyTypeCode'],
                vehicleUsage: this.vehicleUsage,

                numberOfCylinders: this.vehicleData['cylinders'],

                nationality: this.nationality,

                seatingCapacity: this.vehicleData['seats'],
                firstRegistrationDate: this.firstRegistrationDate,
                isGccSpec: this.vehicleData['isGccSpec'],
                isPreviousInsuranceValid: this.previousInsuranceValid,
                isTotalLoss: this.totalLossVehicle,

                driverDOB: this.dob,

                noClaimYears: this.noClaimYears,
                noClaimYearsSelfDec: this.noClaimYearsSelfDec,

                chassisNumber: this.vehicleInfo['chassisNumber'],

                gulfDrivingExperience: this.gulfDrivingExperience,

                trimCode: this.selectedTrim['trimCode']
            }
        },
        getQuotes() {
            this.state = 'getting-quotes';

            $.ajax(qicGetQuotesUrl, {
                method: "post",
                data: JSON.stringify(this.getRequestData()),
                contentType: "application/json"
            })
                    .done((response) => {
                        const auto_quote_modal = $('#modal_auto_quote_form');

                        const quotes = response.quotes;
                        if (quotes.length > 0) {
                            const source = $('#autoquoted-product-list-template').html();
                            const template = Handlebars.compile(source);
                            auto_quote_modal.find('.response').html(
                                    template({'records': response.quotes})
                            );
                        } else {
                            auto_quote_modal.find('.response').html('<span class="error">No quote found for the given details.</span>');
                        }
                    })
                    .fail((xhr) => {
                        $('#modal_auto_quote_form ul.error').show();
                        $('#modal_auto_quote_form ul.error').append('<li>' + xhr.responseText + '</li>');
                    })
                    .always(() => {
                        this.state = 'can-get-quotes'
                    });
        }
    },
    mounted() {
        $.get(qicTrimDetailsUrl, {
            chassisNumber: this.vehicleInfo.chassisNumber,
            makeCode: this.vehicleInfo.makeCode,
            modelCode: this.vehicleInfo.modelCode,
            yearCode: this.vehicleInfo.yearCode,
            trimCode: this.selectedTrim.trimCode
        })
                .done((response) => {
                    this.state = "can-get-quotes";
                    this.vehicleData = response;
                    this.sumInsured = response['value'];
                })
                .fail((xhr) => {
                    this.state = "error";
                    this.errorMessage = xhr.responseText;
                })
    }
}
</script>

<style scoped>

</style>