import { afterEach, describe, expect, it, vi } from 'vitest'
import {
  createApplication,
  createCompany,
  deleteApplication,
  fetchApplications,
  fetchCompanies,
  updateStatus,
} from './api'
import type { NewApplication } from './types'

const API = 'http://localhost:8000'

/**
 * Replace the real `fetch` with a fake that returns `body` and `status`.
 *
 * `vi.spyOn(globalThis, 'fetch')` watches the global `fetch` function,
 * and `mockResolvedValue` makes it return our fake response instead of
 * touching the network. Like a real Response, the fake throws if you
 * call `.json()` on a 204 (which has no body).
 */
function mockFetch(body: unknown, status = 200) {
  return vi.spyOn(globalThis, 'fetch').mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    json: async () => {
      if (status === 204) {
        throw new SyntaxError('Unexpected end of JSON input')
      }
      return body
    },
  } as Response)
}

/** The URL and options of the most recent `fetch` call. */
function lastRequest(fetchMock: ReturnType<typeof mockFetch>) {
  const [url, init] = fetchMock.mock.calls.at(-1)!
  return {
    url: String(url),
    method: init?.method ?? 'GET',
    body: init?.body ? JSON.parse(String(init.body)) : undefined,
  }
}

afterEach(() => {
  vi.restoreAllMocks()
})

describe('fetchApplications', () => {
  it('GETs every application', async () => {
    const fetchMock = mockFetch([])

    await expect(fetchApplications()).resolves.toEqual([])

    expect(lastRequest(fetchMock)).toMatchObject({
      url: `${API}/applications`,
      method: 'GET',
    })
  })

  it('adds a status filter to the URL when given one', async () => {
    const fetchMock = mockFetch([])

    await fetchApplications('offer')

    expect(lastRequest(fetchMock).url).toBe(
      `${API}/applications?status=offer`,
    )
  })
})

describe('createApplication', () => {
  it('POSTs the new application as JSON', async () => {
    const newApplication: NewApplication = {
      company_id: 1,
      role: 'Junior Developer',
      status: 'applied',
      applied_on: '2026-10-01',
    }
    const created = {
      id: 7,
      role: 'Junior Developer',
      status: 'applied',
      applied_on: '2026-10-01',
      company: { id: 1, name: 'Acme' },
    }
    const fetchMock = mockFetch(created, 201)

    await expect(createApplication(newApplication)).resolves.toEqual(
      created,
    )

    expect(lastRequest(fetchMock)).toEqual({
      url: `${API}/applications`,
      method: 'POST',
      body: newApplication,
    })
  })

  it("rejects with the server's error message", async () => {
    mockFetch({ detail: 'Company not found' }, 422)

    await expect(
      createApplication({
        company_id: 999,
        role: 'Junior Developer',
        status: 'applied',
        applied_on: '2026-10-01',
      }),
    ).rejects.toThrow('Company not found')
  })
})

describe('updateStatus', () => {
  it('PATCHes only the status', async () => {
    const fetchMock = mockFetch({})

    await updateStatus(3, 'offer')

    expect(lastRequest(fetchMock)).toEqual({
      url: `${API}/applications/3`,
      method: 'PATCH',
      body: { status: 'offer' },
    })
  })
})

describe('deleteApplication', () => {
  it('DELETEs and does not try to read a body from a 204', async () => {
    const fetchMock = mockFetch(null, 204)

    await expect(deleteApplication(3)).resolves.toBeUndefined()

    expect(lastRequest(fetchMock)).toMatchObject({
      url: `${API}/applications/3`,
      method: 'DELETE',
    })
  })

  it('rejects with a generic message when the error has no detail', async () => {
    mockFetch({}, 500)

    await expect(deleteApplication(3)).rejects.toThrow(
      'Request failed: 500',
    )
  })
})

describe('fetchCompanies', () => {
  it('GETs every company', async () => {
    const companies = [{ id: 1, name: 'Acme' }]
    const fetchMock = mockFetch(companies)

    await expect(fetchCompanies()).resolves.toEqual(companies)

    expect(lastRequest(fetchMock).url).toBe(`${API}/companies`)
  })
})

describe('createCompany', () => {
  it('POSTs the name', async () => {
    const fetchMock = mockFetch({ id: 2, name: 'Globex' }, 201)

    await expect(createCompany('Globex')).resolves.toEqual({
      id: 2,
      name: 'Globex',
    })

    expect(lastRequest(fetchMock)).toEqual({
      url: `${API}/companies`,
      method: 'POST',
      body: { name: 'Globex' },
    })
  })

  it("rejects with the server's error message", async () => {
    mockFetch({ detail: 'Company already exists' }, 409)

    await expect(createCompany('Acme')).rejects.toThrow(
      'Company already exists',
    )
  })
})
