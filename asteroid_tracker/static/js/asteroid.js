// Just for debugging
function p(x) { console.log(x); }

var $ALERTS_WRAPPER = $("#alerts");
var $SUCCESS_ALERT = $ALERTS_WRAPPER.find(".alert-success");
var $ERROR_ALERT = $ALERTS_WRAPPER.find(".alert-danger");

class AsteroidApp {
    constructor(settings) {
        this.settings = settings;
    }

    /*
     * Retrieve target data from the tom_education API, and update the UI
     */
    async update() {
        try {
            var data = await $.get(this.get_absolute_url(this.settings.api_url));
            this.display(data);
        }
        catch(err) {
            this.show_error(err);
        }
    }

    /*
     * Display target/timelapse data from API in the UI
     */
    display(data) {
        // Set name throughout page
        $(".asteroid-name").text(data.target.name);

        var $info_section = $("#asteroid-info");
        // TODO: consider if injecting HTML directly like this is safe against XSS
        var markdown = data.target.extra_fields.target_info || "No information available!";
        var converter = new showdown.Converter();
        $info_section.html(converter.makeHtml(markdown));

        // Timelapses
        var $timelapse_area = $("#asteroid-timelapses");
        var $no_timelapse_area = $("#no-timelapses");
        if (data.timelapses.length > 0) {
            var tl = data.timelapses[0];
            var url = this.get_absolute_url(tl.url);

            $("#timelapse-num-images").text(tl.frames);
            $("#timelapse-last-updated").text(AsteroidApp.format_timestamp(tl.created));

            var $video_el = $timelapse_area.find("video");
            var $img_el = $timelapse_area.find("img");
            $video_el.hide();
            $img_el.hide();

            if (tl.format === "gif") {
                $img_el.attr("src", url);
                $img_el.show();
            }
            else {
                $video_el.attr("src", url);
                $video_el.attr("type", AsteroidApp.get_video_mime(tl.format));
                $video_el.find("a").attr("href", url);
                $video_el.show();
            }

            $timelapse_area.show();
            $no_timelapse_area.hide();
        }
        else {
            $timelapse_area.hide();
            $no_timelapse_area.show();
        }
    }

    get_absolute_url(rel_url) {
        return this.settings.base_url + rel_url;
    }

    /*
     * Return a string representation of a UNIX timestamp
     */
    static format_timestamp(timestamp) {
        return new Date(timestamp * 1000).toLocaleString();
    }

    /*
     * Return the MIME type to use for a <video> element for a timelapse in the
     * given format
     */
    static get_video_mime(format) {
        switch (format) {
            case "mp4":
                return "video/mp4";
            case "webm":
                return "video/webm";
        }
        throw new Error(`Unrecognised video format ${format}`);
    }

    async submit_form($form) {
        $SUCCESS_ALERT.hide();
        $ERROR_ALERT.hide();

        var $form_els = $form.find("input");
        var $email_input = $form.find("input[name=email]");
        var $submit_button = $form.find("input[type=submit]");
        $form_els.prop("disabled", true);

        // Change text of submit button to a loading message
        var old_submit_value = $submit_button.val();
        $submit_button.val("Loading...");

        var email = $email_input.val();
        var url = this.get_absolute_url(this.settings.observe_api_url);
        // Construct start and end dates for observation based on current
        // time
        var start = new Date();
        var end = new Date(start.valueOf() + 7 * 24 * 60 * 60 * 1000);  // + 7 days for end date

        var error = false;
        try {
            var payload = {
                "target": this.settings.target_pk,
                "template_name": this.settings.template_name,
                "facility": this.settings.facility,
                "email": email,
                "overrides": {
                    "start": start.toISOString(),
                    "end": end.toISOString()
                }
            };
            await $.post({
                "url": url,
                "data": JSON.stringify(payload),
                "contentType": "application/json; charset=utf-8"
            });
        }
        catch (err) {
            error = true;
            this.show_error(err);
        }
        finally {
            $form_els.prop("disabled", false);
            $submit_button.val(old_submit_value);
        }

        if (!error) {
            $email_input.val("");
            $SUCCESS_ALERT.show();
        }
    }

    show_error(err) {
        console.error(err);
        if (err.status == 400) {
            var errs = Object.values(err.responseJSON);
            $ERROR_ALERT.html(errs.join("<br />"));
        }
        else {
            $ERROR_ALERT.text("Error connecting to TOM education API");
        }
        $ERROR_ALERT.show();
    }
}

$(document).ready(function() {
    var json_string = $("#asteroid-settings")[0].textContent;
    var settings = JSON.parse(json_string);
    var app = new AsteroidApp(settings);
    $("#submission-form").submit(function(e) {
        e.preventDefault();
        app.submit_form($(this));
    });
    app.update();
});
