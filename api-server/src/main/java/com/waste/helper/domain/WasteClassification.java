package com.waste.helper.domain;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import jakarta.persistence.*;
import jakarta.validation.constraints.*;
import java.io.Serial;
import java.io.Serializable;
import java.time.Instant;
import java.util.HashSet;
import java.util.Set;
import org.hibernate.annotations.Cache;
import org.hibernate.annotations.CacheConcurrencyStrategy;

/**
 * A WasteClassification.
 */
@Entity
@Table(name = "waste_classification")
@Cache(usage = CacheConcurrencyStrategy.READ_WRITE)
@SuppressWarnings("common-java:DuplicatedBlocks")
public class WasteClassification implements Serializable {

    @Serial
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "sequenceGenerator")
    @SequenceGenerator(name = "sequenceGenerator")
    @Column(name = "id")
    private Long id;

    @NotNull
    @Column(name = "detected_class", nullable = false)
    private String detectedClass;

    @NotNull
    @DecimalMin(value = "0")
    @Column(name = "confidence", nullable = false)
    private Float confidence;

    @Column(name = "image_url")
    private String imageUrl;

    @Lob
    @Column(name = "detail_result")
    private String detailResult;

    @NotNull
    @Column(name = "classified_at", nullable = false)
    private Instant classifiedAt;

    @ManyToOne(fetch = FetchType.LAZY)
    private User user;

    @OneToMany(fetch = FetchType.LAZY, mappedBy = "wasteClassification")
    @Cache(usage = CacheConcurrencyStrategy.READ_WRITE)
    @JsonIgnoreProperties(value = { "wasteClassification" }, allowSetters = true)
    private Set<WasteImage> wasteImages = new HashSet<>();

    @OneToMany(fetch = FetchType.LAZY, mappedBy = "wasteClassification")
    @Cache(usage = CacheConcurrencyStrategy.READ_WRITE)
    @JsonIgnoreProperties(value = { "user", "wasteClassification" }, allowSetters = true)
    private Set<Feedback> feedbacks = new HashSet<>();

    // jhipster-needle-entity-add-field - JHipster will add fields here

    public Long getId() {
        return this.id;
    }

    public WasteClassification id(Long id) {
        this.setId(id);
        return this;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getDetectedClass() {
        return this.detectedClass;
    }

    public WasteClassification detectedClass(String detectedClass) {
        this.setDetectedClass(detectedClass);
        return this;
    }

    public void setDetectedClass(String detectedClass) {
        this.detectedClass = detectedClass;
    }

    public Float getConfidence() {
        return this.confidence;
    }

    public WasteClassification confidence(Float confidence) {
        this.setConfidence(confidence);
        return this;
    }

    public void setConfidence(Float confidence) {
        this.confidence = confidence;
    }

    public String getImageUrl() {
        return this.imageUrl;
    }

    public WasteClassification imageUrl(String imageUrl) {
        this.setImageUrl(imageUrl);
        return this;
    }

    public void setImageUrl(String imageUrl) {
        this.imageUrl = imageUrl;
    }

    public String getDetailResult() {
        return this.detailResult;
    }

    public WasteClassification detailResult(String detailResult) {
        this.setDetailResult(detailResult);
        return this;
    }

    public void setDetailResult(String detailResult) {
        this.detailResult = detailResult;
    }

    public Instant getClassifiedAt() {
        return this.classifiedAt;
    }

    public WasteClassification classifiedAt(Instant classifiedAt) {
        this.setClassifiedAt(classifiedAt);
        return this;
    }

    public void setClassifiedAt(Instant classifiedAt) {
        this.classifiedAt = classifiedAt;
    }

    public User getUser() {
        return this.user;
    }

    public void setUser(User user) {
        this.user = user;
    }

    public WasteClassification user(User user) {
        this.setUser(user);
        return this;
    }

    public Set<WasteImage> getWasteImages() {
        return this.wasteImages;
    }

    public void setWasteImages(Set<WasteImage> wasteImages) {
        if (this.wasteImages != null) {
            this.wasteImages.forEach(i -> i.setWasteClassification(null));
        }
        if (wasteImages != null) {
            wasteImages.forEach(i -> i.setWasteClassification(this));
        }
        this.wasteImages = wasteImages;
    }

    public WasteClassification wasteImages(Set<WasteImage> wasteImages) {
        this.setWasteImages(wasteImages);
        return this;
    }

    public WasteClassification addWasteImages(WasteImage wasteImage) {
        this.wasteImages.add(wasteImage);
        wasteImage.setWasteClassification(this);
        return this;
    }

    public WasteClassification removeWasteImages(WasteImage wasteImage) {
        this.wasteImages.remove(wasteImage);
        wasteImage.setWasteClassification(null);
        return this;
    }

    public Set<Feedback> getFeedbacks() {
        return this.feedbacks;
    }

    public void setFeedbacks(Set<Feedback> feedbacks) {
        if (this.feedbacks != null) {
            this.feedbacks.forEach(i -> i.setWasteClassification(null));
        }
        if (feedbacks != null) {
            feedbacks.forEach(i -> i.setWasteClassification(this));
        }
        this.feedbacks = feedbacks;
    }

    public WasteClassification feedbacks(Set<Feedback> feedbacks) {
        this.setFeedbacks(feedbacks);
        return this;
    }

    public WasteClassification addFeedbacks(Feedback feedback) {
        this.feedbacks.add(feedback);
        feedback.setWasteClassification(this);
        return this;
    }

    public WasteClassification removeFeedbacks(Feedback feedback) {
        this.feedbacks.remove(feedback);
        feedback.setWasteClassification(null);
        return this;
    }

    // jhipster-needle-entity-add-getters-setters - JHipster will add getters and setters here

    @Override
    public boolean equals(Object o) {
        if (this == o) {
            return true;
        }
        if (!(o instanceof WasteClassification)) {
            return false;
        }
        return getId() != null && getId().equals(((WasteClassification) o).getId());
    }

    @Override
    public int hashCode() {
        // see https://vladmihalcea.com/how-to-implement-equals-and-hashcode-using-the-jpa-entity-identifier/
        return getClass().hashCode();
    }

    // prettier-ignore
    @Override
    public String toString() {
        return "WasteClassification{" +
            "id=" + getId() +
            ", detectedClass='" + getDetectedClass() + "'" +
            ", confidence=" + getConfidence() +
            ", imageUrl='" + getImageUrl() + "'" +
            ", detailResult='" + getDetailResult() + "'" +
            ", classifiedAt='" + getClassifiedAt() + "'" +
            "}";
    }
}
