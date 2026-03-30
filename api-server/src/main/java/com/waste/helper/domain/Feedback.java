package com.waste.helper.domain;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import jakarta.persistence.*;
import java.io.Serial;
import java.io.Serializable;
import org.hibernate.annotations.Cache;
import org.hibernate.annotations.CacheConcurrencyStrategy;

/**
 * A Feedback.
 */
@Entity
@Table(name = "feedback")
@Cache(usage = CacheConcurrencyStrategy.READ_WRITE)
@SuppressWarnings("common-java:DuplicatedBlocks")
public class Feedback implements Serializable {

    @Serial
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "sequenceGenerator")
    @SequenceGenerator(name = "sequenceGenerator")
    @Column(name = "id")
    private Long id;

    @Column(name = "is_accurate")
    private Boolean isAccurate;

    @Column(name = "corrected_class")
    private String correctedClass;

    @Column(name = "comment")
    private String comment;

    @ManyToOne(fetch = FetchType.LAZY)
    private User user;

    @ManyToOne(fetch = FetchType.LAZY)
    @JsonIgnoreProperties(value = { "user", "wasteImages", "feedbacks" }, allowSetters = true)
    private WasteClassification wasteClassification;

    // jhipster-needle-entity-add-field - JHipster will add fields here

    public Long getId() {
        return this.id;
    }

    public Feedback id(Long id) {
        this.setId(id);
        return this;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Boolean getIsAccurate() {
        return this.isAccurate;
    }

    public Feedback isAccurate(Boolean isAccurate) {
        this.setIsAccurate(isAccurate);
        return this;
    }

    public void setIsAccurate(Boolean isAccurate) {
        this.isAccurate = isAccurate;
    }

    public String getCorrectedClass() {
        return this.correctedClass;
    }

    public Feedback correctedClass(String correctedClass) {
        this.setCorrectedClass(correctedClass);
        return this;
    }

    public void setCorrectedClass(String correctedClass) {
        this.correctedClass = correctedClass;
    }

    public String getComment() {
        return this.comment;
    }

    public Feedback comment(String comment) {
        this.setComment(comment);
        return this;
    }

    public void setComment(String comment) {
        this.comment = comment;
    }

    public User getUser() {
        return this.user;
    }

    public void setUser(User user) {
        this.user = user;
    }

    public Feedback user(User user) {
        this.setUser(user);
        return this;
    }

    public WasteClassification getWasteClassification() {
        return this.wasteClassification;
    }

    public void setWasteClassification(WasteClassification wasteClassification) {
        this.wasteClassification = wasteClassification;
    }

    public Feedback wasteClassification(WasteClassification wasteClassification) {
        this.setWasteClassification(wasteClassification);
        return this;
    }

    // jhipster-needle-entity-add-getters-setters - JHipster will add getters and setters here

    @Override
    public boolean equals(Object o) {
        if (this == o) {
            return true;
        }
        if (!(o instanceof Feedback)) {
            return false;
        }
        return getId() != null && getId().equals(((Feedback) o).getId());
    }

    @Override
    public int hashCode() {
        // see https://vladmihalcea.com/how-to-implement-equals-and-hashcode-using-the-jpa-entity-identifier/
        return getClass().hashCode();
    }

    // prettier-ignore
    @Override
    public String toString() {
        return "Feedback{" +
            "id=" + getId() +
            ", isAccurate='" + getIsAccurate() + "'" +
            ", correctedClass='" + getCorrectedClass() + "'" +
            ", comment='" + getComment() + "'" +
            "}";
    }
}
