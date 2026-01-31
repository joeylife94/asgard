package com.heimdall.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Request DTO for redrive operation.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class RedriveRequest {
    /**
     * Optional reason for the redrive (for audit purposes).
     */
    private String reason;
}
